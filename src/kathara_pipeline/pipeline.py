from __future__ import annotations

import csv
import json
import logging
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .checker_runner import CheckerRunner
from .codex_runner import CodexRunner, redact_command
from .config import PipelineConfig
from .correction_generator import CorrectionGenerator
from .exceptions import (
    PipelineError,
    PipelineJobError,
    PreflightError,
    PromptDiscoveryError,
    UnsafePathError,
)
from .lab_generator import LabGenerator
from .lab_validator import LabValidator
from .models import (
    CommandResult,
    JobPaths,
    JobStatus,
    JobSummary,
    PipelineSummary,
    PromptRecord,
    ResourceFiles,
)
from .paths import (
    assert_safe_destructive_path,
    build_job_paths,
    ensure_generated_root_managed,
    safe_rmtree,
)
from .preflight import PreflightReport, run_preflight
from .prompt_discovery import discover_prompts
from .result_parser import ResultParser
from .state_store import StateStore, read_json, sha256_file, write_json_atomic
from .yaml_validator import YamlValidator


LOGGER = logging.getLogger("kathara_pipeline")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _duration(started: float) -> float:
    return round(time.monotonic() - started, 6)


def _error_text(exc: BaseException) -> str:
    details = getattr(exc, "details", ())
    if details:
        return f"{exc}: {'; '.join(str(item) for item in details)}"
    return str(exc)


def _redacted_command(command: tuple[str, ...] | list[str]) -> list[str]:
    return redact_command(command)


def _command_metadata(result: CommandResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "command": _redacted_command(result.command),
        "return_code": result.return_code,
        "duration_seconds": result.duration_seconds,
        "timed_out": result.timed_out,
        "malformed_json_lines": list(result.malformed_json_lines),
    }


class Pipeline:
    """Sequential orchestrator for all discovered prompt jobs."""

    def __init__(
        self,
        config: PipelineConfig,
        *,
        emit: Callable[[str], None] = print,
    ) -> None:
        self.config = config
        self.emit = emit
        self.codex_runner = CodexRunner(
            command=config.codex.command,
            sandbox=config.codex.sandbox,
            timeout_seconds=config.codex.timeout_seconds,
        )
        self.lab_generator = LabGenerator(self.codex_runner)
        self.correction_generator = CorrectionGenerator(self.codex_runner)
        self.lab_validator = LabValidator()
        self.checker_runner = CheckerRunner(
            timeout_seconds=config.checker.timeout_seconds,
            report_type=config.checker.report_type,
            no_cache=config.checker.no_cache,
        )
        self.result_parser = ResultParser()

    def discover(self) -> list[PromptRecord]:
        return discover_prompts(self.config.paths.prompts)

    def preflight(
        self, prompts: list[PromptRecord], *, dry_run: bool = False
    ) -> PreflightReport:
        report = run_preflight(self.config, prompts, dry_run=dry_run)
        for warning in report.warnings:
            self.emit(f"AVVISO: {warning}")
        report.require_ok()
        return report

    def _select(
        self, prompts: list[PromptRecord], prompt_name: str | None
    ) -> list[PromptRecord]:
        if prompt_name is None:
            return prompts
        selected = [prompt for prompt in prompts if prompt.name == prompt_name]
        if not selected:
            raise PromptDiscoveryError(
                f"Prompt non trovato in {self.config.paths.prompts}: {prompt_name}"
            )
        return selected

    def _existing_job_is_current(
        self,
        prompt: PromptRecord,
        paths: JobPaths,
        resources: ResourceFiles,
    ) -> bool:
        if not self.config.processing.skip_completed or prompt.prompt_hash is None:
            return False
        try:
            manifest = read_json(paths.manifest)
            report = read_json(paths.reports / "result-summary.json")
        except PipelineJobError:
            return False
        if not manifest or not report:
            return False
        if manifest.get("status") not in {JobStatus.PASSED.value, JobStatus.FAILED.value}:
            return False
        expected = {
            "pipeline_version": __version__,
            "prompt_sha256": prompt.prompt_hash,
            "skill_sha256": resources.skill_hash,
            "schema_sha256": resources.schema_hash,
        }
        if any(manifest.get(key) != value for key, value in expected.items()):
            return False
        if report.get("status") != manifest.get("status"):
            return False
        count_keys = ("total_tests", "passed_tests", "failed_tests")
        if not all(
            isinstance(report.get(key), int) and not isinstance(report.get(key), bool)
            for key in count_keys
        ):
            return False
        if report["total_tests"] != report["passed_tests"] + report["failed_tests"]:
            return False
        expected_status = "passed" if report["failed_tests"] == 0 else "failed"
        if report["status"] != expected_status:
            return False
        reports_found = report.get("reports_found")
        reports_missing = report.get("reports_missing")
        if not isinstance(reports_found, list) or len(reports_found) < 3:
            return False
        if reports_missing not in ([], ()):  # JSON persists tuples as lists.
            return False
        raw_reports_root = (paths.reports / "checker").resolve()
        for relative_name in reports_found:
            if not isinstance(relative_name, str) or not relative_name:
                return False
            candidate = (raw_reports_root / relative_name).resolve()
            if not candidate.is_relative_to(raw_reports_root) or not candidate.is_file():
                return False
            try:
                with candidate.open("r", encoding="utf-8-sig", newline="") as stream:
                    if not stream.readline().strip():
                        return False
            except (OSError, UnicodeError):
                return False
        correction_hash = manifest.get("correction_sha256")
        if not isinstance(correction_hash, str) or not paths.correction.is_file():
            return False
        try:
            if sha256_file(paths.correction) != correction_hash:
                return False
        except OSError:
            return False
        checker_return_code = report.get("checker_process_return_code")
        if not isinstance(checker_return_code, int) or isinstance(checker_return_code, bool):
            return False
        try:
            parsed = self.result_parser.parse(
                checker_run=paths.checker_run,
                labs_dir=paths.labs_dir,
                candidate=paths.candidate,
                checker_return_code=checker_return_code,
            )
        except PipelineJobError:
            return False
        if (
            parsed.total_tests,
            parsed.passed_tests,
            parsed.failed_tests,
        ) != (
            report["total_tests"],
            report["passed_tests"],
            report["failed_tests"],
        ):
            return False
        return True

    def _skip_reason(
        self,
        prompt: PromptRecord,
        paths: JobPaths,
        resources: ResourceFiles,
        *,
        force: bool,
    ) -> str | None:
        if prompt.empty:
            return "prompt vuoto"
        if not force and self._existing_job_is_current(prompt, paths, resources):
            return "risultato completo e invariato"
        return None

    def _dry_run(
        self,
        prompts: list[PromptRecord],
        resources: ResourceFiles,
        *,
        force: bool,
    ) -> None:
        self.emit(f"Dry-run: {len(prompts)} prompt considerati.")
        for index, prompt in enumerate(prompts, 1):
            paths = build_job_paths(self.config.paths.generated_labs, prompt.lab_id)
            reason = self._skip_reason(prompt, paths, resources, force=force)
            self.emit(f"{index}. {prompt.name} -> {prompt.lab_id}")
            if reason == "risultato completo e invariato":
                self.emit(f"   stato previsto: skipped ({reason})")
                continue
            self.emit("   directory iniziali da creare:")
            for directory in (
                paths.root,
                paths.correction_dir,
                paths.reports,
                paths.logs,
            ):
                self.emit(f"     - {directory}")
            if paths.root.exists() or paths.root.is_symlink():
                try:
                    replacement = assert_safe_destructive_path(
                        paths.root,
                        self.config.paths.generated_labs,
                        project_root=self.config.paths.project_root,
                    )
                    if not replacement.is_dir():
                        raise UnsafePathError(
                            f"Il path job esistente non è una directory: {replacement}"
                        )
                except UnsafePathError as exc:
                    raise PreflightError(
                        "Dry-run bloccato da un path job non sostituibile.",
                        (f"{prompt.name}: {exc}",),
                    ) from exc
                self.emit(
                    "   AVVISO: la directory job esistente verrebbe eliminata e ricreata: "
                    f"{paths.root}"
                )
            if prompt.decode_error:
                self.emit(f"   stato previsto: error ({prompt.decode_error})")
                continue
            if reason:
                self.emit(f"   stato previsto: skipped ({reason})")
                continue
            self.emit("   directory delle fasi da creare e poi, per i workspace, rimuovere:")
            for directory in (
                paths.source,
                paths.lab_workspace,
                paths.correction_workspace,
                paths.checker_run,
                paths.labs_dir,
                paths.candidate,
            ):
                self.emit(f"     - {directory}")
            lab_instruction = self.lab_generator._instruction()
            correction_instruction = self.correction_generator._instruction(
                skill_name=resources.skill_path.name,
                schema_name=resources.schema_path.name,
                has_examples=resources.examples_path is not None,
            )
            lab_command = self.codex_runner.build_command(
                workspace=paths.lab_workspace,
                output_last_message=paths.lab_workspace / ".codex-last-message.txt",
                instruction=lab_instruction,
            )
            correction_command = self.codex_runner.build_command(
                workspace=paths.correction_workspace,
                output_last_message=paths.correction_workspace / ".codex-last-message.txt",
                instruction=correction_instruction,
            )
            checker_command = self.checker_runner.build_command(
                correction_path=paths.correction,
                labs_directory=paths.labs_dir,
            )
            self.emit(f"   Codex lab argv: {json.dumps(lab_command, ensure_ascii=False)}")
            self.emit(
                f"   Codex correction argv: {json.dumps(correction_command, ensure_ascii=False)}"
            )
            self.emit(f"   checker argv: {json.dumps(checker_command, ensure_ascii=False)}")

    def _initial_manifest(
        self,
        prompt: PromptRecord,
        resources: ResourceFiles,
        started_at: str,
    ) -> dict[str, Any]:
        return {
            "pipeline_version": __version__,
            "lab_id": prompt.lab_id,
            "original_prompt_name": prompt.name,
            "original_prompt_path": str(prompt.path),
            "prompt_sha256": prompt.prompt_hash,
            "skill_sha256": resources.skill_hash,
            "schema_sha256": resources.schema_hash,
            "schema_mode": resources.schema_mode,
            "started_at": started_at,
            "finished_at": None,
            "duration_seconds": None,
            "status": JobStatus.DISCOVERED.value,
            "test_result": None,
            "correction_sha256": None,
            "phases": [{"name": "discovered", "at": started_at}],
            "errors": [],
        }

    @staticmethod
    def _phase(store: StateStore, manifest: dict[str, Any], name: str, **fields: Any) -> None:
        manifest.setdefault("phases", []).append({"name": name, "at": _utc_now()})
        manifest.update(fields)
        store.write(manifest)
        LOGGER.info("Fase job completata: %s", name)

    def _prepare_new_job(self, paths: JobPaths) -> None:
        ensure_generated_root_managed(self.config.paths.generated_labs, initialize=True)
        if paths.root.exists() or paths.root.is_symlink():
            safe_rmtree(
                paths.root,
                self.config.paths.generated_labs,
                project_root=self.config.paths.project_root,
            )
        paths.logs.mkdir(parents=True, exist_ok=True)
        paths.reports.mkdir(parents=True, exist_ok=True)
        paths.correction_dir.mkdir(parents=True, exist_ok=True)

    def _cleanup_workspaces(self, paths: JobPaths) -> None:
        workspaces = paths.root / ".workspaces"
        if workspaces.exists() or workspaces.is_symlink():
            safe_rmtree(
                workspaces,
                self.config.paths.generated_labs,
                project_root=self.config.paths.project_root,
            )

    def _write_prompt_copy(self, prompt: PromptRecord, paths: JobPaths) -> None:
        if prompt.content is not None:
            paths.prompt.write_text(prompt.content, encoding="utf-8")

    def _job_handler(self, paths: JobPaths) -> logging.Handler:
        handler = logging.FileHandler(paths.logs / "job.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        LOGGER.addHandler(handler)
        return handler

    def process_single_prompt(
        self,
        prompt: PromptRecord,
        resources: ResourceFiles,
        *,
        force: bool,
    ) -> JobSummary:
        paths = build_job_paths(self.config.paths.generated_labs, prompt.lab_id)
        reason = self._skip_reason(prompt, paths, resources, force=force)
        if reason == "risultato completo e invariato":
            return JobSummary(prompt.lab_id, prompt.name, JobStatus.SKIPPED, skip_reason=reason)

        started_monotonic = time.monotonic()
        started_at = _utc_now()
        store = StateStore(paths.manifest)
        manifest = self._initial_manifest(prompt, resources, started_at)
        handler: logging.Handler | None = None
        lab_generated = False
        lab_tested = False
        active_process_field: str | None = None

        try:
            self._prepare_new_job(paths)
            store.write(manifest)
            self._write_prompt_copy(prompt, paths)
            self._phase(store, manifest, "job_created")
            handler = self._job_handler(paths)
            LOGGER.info("Avvio job %s (%s)", prompt.name, prompt.lab_id)

            if prompt.decode_error:
                raise PipelineJobError(prompt.decode_error)
            if reason == "prompt vuoto":
                finished_at = _utc_now()
                elapsed = _duration(started_monotonic)
                manifest.update(
                    {
                        "status": JobStatus.SKIPPED.value,
                        "skip_reason": reason,
                        "finished_at": finished_at,
                        "duration_seconds": elapsed,
                    }
                )
                self._phase(store, manifest, "skipped")
                return JobSummary(
                    prompt.lab_id,
                    prompt.name,
                    JobStatus.SKIPPED,
                    duration_seconds=elapsed,
                    skip_reason=reason,
                )

            lab_instruction = self.lab_generator._instruction()
            planned_lab_command = self.codex_runner.build_command(
                workspace=paths.lab_workspace,
                output_last_message=paths.lab_workspace / ".codex-last-message.txt",
                instruction=lab_instruction,
            )
            self._phase(
                store,
                manifest,
                "lab_generation_started",
                codex_lab_planned={
                    "command": _redacted_command(planned_lab_command),
                    "workspace": str(paths.lab_workspace),
                },
            )
            active_process_field = "codex_lab"
            lab_command_result = self.lab_generator.generate(prompt, paths)
            active_process_field = None
            lab_generated = True
            self._phase(
                store,
                manifest,
                "lab_generated",
                codex_lab=_command_metadata(lab_command_result),
            )

            lab_validation = self.lab_validator.validate(paths.source, prompt.content or "")
            if not lab_validation.valid:
                from .exceptions import LabValidationError

                raise LabValidationError("Validazione statica del laboratorio fallita", lab_validation.errors)
            self._phase(store, manifest, "lab_validated")

            correction_instruction = self.correction_generator._instruction(
                skill_name=resources.skill_path.name,
                schema_name=resources.schema_path.name,
                has_examples=resources.examples_path is not None,
            )
            planned_correction_command = self.codex_runner.build_command(
                workspace=paths.correction_workspace,
                output_last_message=paths.correction_workspace / ".codex-last-message.txt",
                instruction=correction_instruction,
            )
            self._phase(
                store,
                manifest,
                "correction_generation_started",
                codex_correction_planned={
                    "command": _redacted_command(planned_correction_command),
                    "workspace": str(paths.correction_workspace),
                },
            )
            active_process_field = "codex_correction"
            correction_command_result = self.correction_generator.generate(
                prompt, paths, resources
            )
            active_process_field = None
            self._phase(
                store,
                manifest,
                "correction_generated",
                codex_correction=_command_metadata(correction_command_result),
            )

            yaml_validation = YamlValidator(
                resources.schema_path, resources.skill_path
            ).validate(
                paths.correction,
                paths.source,
                paths.root,
            )
            if not yaml_validation.valid:
                from .exceptions import SemanticValidationError

                raise SemanticValidationError(
                    "Validazione di correction.yaml fallita", yaml_validation.errors
                )
            correction_hash = sha256_file(paths.correction)
            self._phase(
                store,
                manifest,
                "correction_validated",
                correction_sha256=correction_hash,
                yaml_validation_mode=yaml_validation.mode,
            )

            self._phase(store, manifest, "checker_copy_started")
            copied_hashes = self.checker_runner.prepare_candidate(paths)
            self._phase(
                store,
                manifest,
                "checker_prepared",
                checker_copy={
                    "files": copied_hashes,
                    "candidate": str(paths.candidate),
                },
            )
            checker_command = self.checker_runner.build_command(
                correction_path=paths.correction,
                labs_directory=paths.labs_dir,
            )
            checker_process: dict[str, Any] = {
                "command": checker_command,
                "working_directory": str(paths.checker_run),
            }
            self._phase(
                store,
                manifest,
                "checker_execution_started",
                checker_process=checker_process,
            )
            lab_tested = True
            active_process_field = "checker_process"
            checker_result = self.checker_runner.run(paths, prepared=True)
            active_process_field = None
            checker_process.update(
                {
                    "return_code": checker_result.return_code,
                    "duration_seconds": checker_result.duration_seconds,
                }
            )
            self._phase(store, manifest, "checker_executed", checker_process=checker_process)

            metrics = self.result_parser.parse_and_store(paths, checker_result)
            self._phase(store, manifest, "reports_parsed")
            status = JobStatus.PASSED if metrics.failed_tests == 0 else JobStatus.FAILED
            elapsed = _duration(started_monotonic)
            finished_at = _utc_now()
            report_payload = {
                "lab_id": prompt.lab_id,
                "status": status.value,
                **metrics.to_dict(),
                "checker_duration_seconds": checker_result.duration_seconds,
                "checker_command": list(checker_result.command),
                "checker_working_directory": str(paths.checker_run),
            }
            write_json_atomic(paths.reports / "result-summary.json", report_payload)
            manifest.update(
                {
                    "status": status.value,
                    "test_result": metrics.to_dict(),
                    "finished_at": finished_at,
                    "duration_seconds": elapsed,
                    "checker_process": checker_process,
                }
            )
            self._phase(store, manifest, "result_saved")
            self._phase(store, manifest, "manifest_updated")
            self._phase(store, manifest, "completed")
            return JobSummary(
                lab_id=prompt.lab_id,
                prompt_file=prompt.name,
                status=status,
                total_tests=metrics.total_tests,
                passed_tests=metrics.passed_tests,
                failed_tests=metrics.failed_tests,
                pass_percentage=metrics.pass_percentage,
                duration_seconds=elapsed,
                lab_generated=True,
                lab_tested=True,
            )
        except Exception as exc:
            LOGGER.exception("Errore durante il job %s", prompt.name)
            elapsed = _duration(started_monotonic)
            message = _error_text(exc)
            if (
                active_process_field is not None
                and isinstance(exc, PipelineJobError)
                and exc.process_metadata is not None
            ):
                manifest[active_process_field] = dict(exc.process_metadata)
                if active_process_field == "checker_process":
                    try:
                        reports_found, reports_missing = self.result_parser.report_inventory(paths)
                        checker_status = (
                            "timed_out"
                            if bool(exc.process_metadata.get("timed_out"))
                            else "process_error"
                        )
                        diagnostics = {
                            "total_tests": None,
                            "passed_tests": None,
                            "failed_tests": None,
                            "pass_percentage": None,
                            "failure_categories": {},
                            "checker_process_return_code": exc.process_metadata.get(
                                "return_code"
                            ),
                            "checker_execution_status": checker_status,
                            "reports_found": reports_found,
                            "reports_missing": reports_missing,
                        }
                        manifest["test_result"] = diagnostics
                        paths.reports.mkdir(parents=True, exist_ok=True)
                        write_json_atomic(
                            paths.reports / "result-summary.json",
                            {
                                "lab_id": prompt.lab_id,
                                "status": JobStatus.ERROR.value,
                                **diagnostics,
                                "checker_return_code": exc.process_metadata.get(
                                    "return_code"
                                ),
                                "checker_duration_seconds": exc.process_metadata.get(
                                    "duration_seconds"
                                ),
                                "checker_command": exc.process_metadata.get("command", []),
                                "checker_working_directory": exc.process_metadata.get(
                                    "working_directory"
                                ),
                                "error_message": message,
                            },
                        )
                    except Exception:
                        LOGGER.exception(
                            "Impossibile salvare il report tecnico del checker per %s",
                            prompt.name,
                        )
            report_diagnostics = getattr(exc, "report_diagnostics", None)
            if isinstance(report_diagnostics, dict):
                manifest["test_result"] = dict(report_diagnostics)
            manifest.update(
                {
                    "status": JobStatus.ERROR.value,
                    "finished_at": _utc_now(),
                    "duration_seconds": elapsed,
                    "errors": [message],
                }
            )
            try:
                if paths.root.is_dir() and not paths.root.is_symlink():
                    paths.logs.mkdir(parents=True, exist_ok=True)
                    self._phase(store, manifest, "error")
            except Exception:
                LOGGER.exception("Impossibile aggiornare il manifest di %s", prompt.name)
            return JobSummary(
                lab_id=prompt.lab_id,
                prompt_file=prompt.name,
                status=JobStatus.ERROR,
                duration_seconds=elapsed,
                error_message=message,
                lab_generated=lab_generated,
                lab_tested=lab_tested,
            )
        finally:
            try:
                self._cleanup_workspaces(paths)
            except Exception:
                LOGGER.exception("Pulizia workspace fallita per %s", prompt.name)
            if handler is not None:
                LOGGER.removeHandler(handler)
                handler.close()

    def _build_summary(
        self,
        jobs: list[JobSummary],
        started_at: str,
        started_monotonic: float,
        prompts_found: int,
    ) -> PipelineSummary:
        counts = {status.value: 0 for status in JobStatus if status.terminal}
        for job in jobs:
            counts[job.status.value] += 1
        return PipelineSummary(
            pipeline_version=__version__,
            started_at=started_at,
            finished_at=_utc_now(),
            duration_seconds=_duration(started_monotonic),
            prompts_found=prompts_found,
            labs_generated=sum(job.lab_generated for job in jobs),
            labs_tested=sum(job.lab_tested for job in jobs),
            counts=counts,
            jobs=jobs,
        )

    def _write_pipeline_summary(self, summary: PipelineSummary) -> None:
        root = self.config.paths.generated_labs
        write_json_atomic(root / "pipeline-summary.json", summary.to_dict())
        csv_path = root / "pipeline-summary.csv"
        temporary = root / ".pipeline-summary.csv.tmp"
        try:
            with temporary.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=[
                        "lab_id",
                        "prompt_file",
                        "status",
                        "total_tests",
                        "passed_tests",
                        "failed_tests",
                        "pass_percentage",
                        "duration_seconds",
                        "error_message",
                        "skip_reason",
                    ],
                )
                writer.writeheader()
                for job in summary.jobs:
                    row = job.to_dict()
                    writer.writerow({key: row.get(key) for key in writer.fieldnames})
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, csv_path)
        finally:
            temporary.unlink(missing_ok=True)

    def _print_summary(self, summary: PipelineSummary) -> None:
        self.emit("Pipeline completata.")
        self.emit(f"Prompt trovati: {summary.prompts_found}")
        self.emit(f"Laboratori generati: {summary.labs_generated}")
        self.emit(f"Laboratori testati: {summary.labs_tested}")
        for label in ("passed", "failed", "error", "skipped"):
            self.emit(f"{label.capitalize()}: {summary.counts[label]}")

    def run(
        self,
        *,
        prompt_name: str | None = None,
        force: bool = False,
        dry_run: bool = False,
    ) -> PipelineSummary | None:
        all_prompts = self.discover()
        report = self.preflight(all_prompts, dry_run=dry_run)
        selected = self._select(all_prompts, prompt_name)
        effective_force = force or self.config.processing.force
        if dry_run:
            self._dry_run(selected, report.resources, force=effective_force)
            return None

        started_monotonic = time.monotonic()
        started_at = _utc_now()
        root = self.config.paths.generated_labs
        ensure_generated_root_managed(root, initialize=True)
        file_handler = logging.FileHandler(root / "pipeline.log", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        previous_log_level = LOGGER.level
        LOGGER.setLevel(logging.INFO)
        LOGGER.addHandler(file_handler)
        jobs: list[JobSummary] = []
        try:
            LOGGER.info("Avvio pipeline con %d prompt selezionati", len(selected))
            for index, prompt in enumerate(selected):
                self.emit(f"Elaborazione: {prompt.name}")
                try:
                    job = self.process_single_prompt(
                        prompt,
                        report.resources,
                        force=effective_force,
                    )
                except Exception as exc:
                    LOGGER.exception("Errore non recuperabile nel job %s", prompt.name)
                    job = JobSummary(
                        lab_id=prompt.lab_id,
                        prompt_file=prompt.name,
                        status=JobStatus.ERROR,
                        error_message=_error_text(exc),
                    )
                jobs.append(job)
                self.emit(f"  {prompt.lab_id}: {job.status.value}")
                LOGGER.info("Job %s terminato con stato %s", prompt.lab_id, job.status.value)
                if (
                    job.status == JobStatus.ERROR
                    and not self.config.processing.continue_on_error
                    and prompt.decode_error is None
                ):
                    self.emit("Interruzione: continue_on_error è disattivo.")
                    for remaining in selected[index + 1 :]:
                        jobs.append(
                            JobSummary(
                                lab_id=remaining.lab_id,
                                prompt_file=remaining.name,
                                status=JobStatus.SKIPPED,
                                skip_reason=(
                                    "non elaborato dopo un error con continue_on_error disattivo"
                                ),
                            )
                        )
                    break
            summary = self._build_summary(
                jobs,
                started_at,
                started_monotonic,
                prompts_found=len(selected),
            )
            self._write_pipeline_summary(summary)
            self._print_summary(summary)
            LOGGER.info("Pipeline completata: %s", summary.counts)
            return summary
        finally:
            LOGGER.removeHandler(file_handler)
            file_handler.close()
            LOGGER.setLevel(previous_log_level)


def exit_code_for_summary(summary: PipelineSummary | None) -> int:
    if summary is None:
        return 0
    if summary.counts.get(JobStatus.ERROR.value, 0):
        return 2
    if summary.counts.get(JobStatus.FAILED.value, 0):
        return 1
    return 0
