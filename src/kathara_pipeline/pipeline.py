from __future__ import annotations

import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .checker_runner import CheckerRunner
from .comparator import compare_variants, write_comparison
from .config import PipelineConfig
from .correction_generator import CorrectionGenerator
from .correction_validator import CorrectionValidator
from .evaluation_spec_generator import EvaluationSpecGenerator
from .exceptions import KatharaFrameworkError, ReportParsingError
from .lab_generator import LabGenerator
from .lab_validator import LabValidator
from .models import (
    ComparisonOutcome,
    ExperimentSummary,
    JobStatus,
    PipelineSummary,
    PromptRecord,
    ResourceFiles,
    Variant,
    VariantPaths,
    VariantSummary,
)
from .paths import build_experiment_paths, ensure_output_root, safe_rmtree
from .preflight import PreflightResult, run_preflight
from .prompt_discovery import discover_prompts
from .report_aggregator import write_aggregate
from .result_parser import parse_checker_results
from .runner_factory import build_runner
from .state_store import read_json, sha256_file, write_json_atomic

PIPELINE_VERSION = "0.4.1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _metadata(result) -> dict[str, Any]:
    return {
        "command": list(result.command),
        "return_code": result.return_code,
        "duration_seconds": result.duration_seconds,
        "timed_out": result.timed_out,
    }


class Pipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.runner = build_runner(config.generation)
        self.lab_generator = LabGenerator(self.runner, config.generation.timeout_seconds)
        self.evaluation_spec_generator = EvaluationSpecGenerator(self.runner, config.generation.timeout_seconds)
        self.correction_generator = CorrectionGenerator(self.runner, config.generation.timeout_seconds)
        self.lab_validator = LabValidator()
        self.correction_validator = CorrectionValidator()
        self.checker = CheckerRunner(
            timeout_seconds=config.checker.timeout_seconds,
            no_cache=config.checker.no_cache,
            report_type=config.checker.report_type,
        )

    def discover(self, prompts_dir: Path) -> list[PromptRecord]:
        return discover_prompts(prompts_dir)

    def preflight(self, prompts_dir: Path, prompts: list[PromptRecord], *, dry_run: bool) -> PreflightResult:
        return run_preflight(self.config, prompts_dir, prompts, dry_run=dry_run)

    def _identity(self, prompt: PromptRecord, resources: ResourceFiles) -> dict[str, Any]:
        return {
            "pipeline_version": PIPELINE_VERSION,
            "prompt_sha256": prompt.prompt_hash,
            "creation_skill_sha256": resources.creation_skill_hash,
            "checker_skill_sha256": resources.checker_skill_hash,
            "checker_schema_sha256": resources.checker_schema_hash,
            "provider": self.config.generation.provider,
            "command": self.config.generation.command,
            "model": self.config.generation.model,
            "reasoning_effort": self.config.generation.reasoning_effort,
            "sandbox": self.config.generation.sandbox,
            "checker_runtime": "kathara-lab-checker==0.1.14",
            "checker_report_type": self.config.checker.report_type,
        }

    def _can_skip(self, paths, identity: dict[str, Any]) -> ExperimentSummary | None:
        if self.config.processing.force or not self.config.processing.skip_completed:
            return None
        saved = read_json(paths.experiment_manifest)
        if not saved or saved.get("identity") != identity or not saved.get("complete"):
            return None
        comparison = read_json(paths.comparison)
        a = read_json(paths.with_skill.manifest)
        b = read_json(paths.without_skill.manifest)
        if not comparison or not a or not b:
            return None

        def restore(data: dict[str, Any], variant: Variant) -> VariantSummary:
            metrics = data.get("metrics") or {}
            return VariantSummary(
                experiment_id=data.get("experiment_id", paths.root.name),
                prompt_file=data.get("prompt_file", paths.prompt.name),
                variant=variant,
                status=JobStatus(data.get("status", "error")),
                lab_generated=bool(data.get("lab_generated")),
                static_validation_passed=bool(data.get("static_validation_passed")),
                checker_attempted=bool(data.get("checker_attempted")),
                checker_completed=bool(data.get("checker_completed")),
                total_tests=metrics.get("total_tests"),
                passed_tests=metrics.get("passed_tests"),
                failed_tests=metrics.get("failed_tests"),
                pass_percentage=metrics.get("pass_percentage"),
                generation_duration_seconds=(data.get("generation") or {}).get("duration_seconds"),
                checker_duration_seconds=(data.get("checker") or {}).get("duration_seconds"),
                error_message=(data.get("errors") or [None])[-1] if data.get("errors") else None,
                skip_reason="unchanged completed paired experiment",
            )
        try:
            outcome = ComparisonOutcome(comparison["outcome"])
        except Exception:
            return None
        return ExperimentSummary(
            paths.root.name,
            saved.get("prompt_file", paths.prompt.name),
            saved.get("evaluation_spec_generated", False),
            paths.correction.is_file(),
            saved.get("canonical_correction_sha256"),
            restore(a, Variant.WITH_SKILL),
            restore(b, Variant.WITHOUT_SKILL),
            outcome,
            comparison.get("reason"),
        )

    def _reset_experiment(self, paths) -> None:
        if paths.root.exists():
            safe_rmtree(paths.root, self.config.paths.output)
        paths.root.mkdir(parents=True)

    def _base_variant_manifest(self, prompt: PromptRecord, variant: Variant, resources: ResourceFiles) -> dict[str, Any]:
        return {
            "pipeline_version": PIPELINE_VERSION,
            "experiment_id": prompt.experiment_id,
            "prompt_file": prompt.name,
            "prompt_sha256": prompt.prompt_hash,
            "variant": variant.value,
            "creation_skill_enabled": variant is Variant.WITH_SKILL,
            "creation_skill_sha256": resources.creation_skill_hash if variant is Variant.WITH_SKILL else None,
            "checker_skill_sha256": resources.checker_skill_hash,
            "checker_schema_sha256": resources.checker_schema_hash,
            "canonical_correction_sha256": None,
            "generation_provider": self.config.generation.provider,
            "generation_command": self.config.generation.command,
            "generation_model": self.config.generation.model,
            "generation_reasoning_effort": self.config.generation.reasoning_effort,
            "lab_generated": False,
            "static_validation_passed": False,
            "checker_attempted": False,
            "checker_completed": False,
            "status": JobStatus.DISCOVERED.value,
            "generation": None,
            "checker": None,
            "metrics": None,
            "phases": [{"name": "discovered", "at": _utc_now()}],
            "errors": [],
        }

    def _phase(self, manifest: dict[str, Any], name: str) -> None:
        manifest.setdefault("phases", []).append({"name": name, "at": _utc_now()})

    def _write_variant(self, path: Path, manifest: dict[str, Any]) -> None:
        write_json_atomic(path, manifest)

    def _generate_variant(
        self, prompt: PromptRecord, variant: Variant, paths: VariantPaths, resources: ResourceFiles
    ) -> tuple[VariantSummary, dict[str, Any]]:
        manifest = self._base_variant_manifest(prompt, variant, resources)
        summary = VariantSummary(prompt.experiment_id, prompt.name, variant, JobStatus.ERROR)
        paths.root.mkdir(parents=True, exist_ok=True)
        paths.logs.mkdir(parents=True, exist_ok=True)
        paths.reports.mkdir(parents=True, exist_ok=True)
        self._phase(manifest, "lab_generation_started")
        try:
            result = self.lab_generator.generate(paths=paths, prompt_text=prompt.content or "", variant=variant, resources=resources)
            manifest["generation"] = _metadata(result)
            manifest["lab_generated"] = True
            summary.lab_generated = True
            summary.generation_duration_seconds = result.duration_seconds
            self._phase(manifest, "lab_generated")
            validation = self.lab_validator.validate(paths.source, prompt.content or "")
            if not validation.valid:
                raise ValueError("Static lab validation failed: " + "; ".join(validation.errors))
            manifest["static_validation_passed"] = True
            summary.static_validation_passed = True
            self._phase(manifest, "static_validation_passed")
            manifest["status"] = "generated"
            summary.status = JobStatus.DISCOVERED
        except Exception as exc:
            manifest["errors"].append(str(exc))
            manifest["status"] = JobStatus.ERROR.value
            summary.status = JobStatus.ERROR
            summary.error_message = str(exc)
            self._phase(manifest, "error")
        self._write_variant(paths.manifest, manifest)
        return summary, manifest

    def _evaluate_variant(
        self,
        prompt: PromptRecord,
        paths: VariantPaths,
        summary: VariantSummary,
        manifest: dict[str, Any],
        correction_hash: str,
    ) -> VariantSummary:
        manifest["canonical_correction_sha256"] = correction_hash
        if not summary.static_validation_passed:
            self._write_variant(paths.manifest, manifest)
            return summary
        try:
            self.checker.prepare_candidate(paths.source, paths)
            # Validate copied candidate as a relocation-safety sanity check.
            copied_validation = self.lab_validator.validate(paths.candidate, prompt.content or "")
            if not copied_validation.valid:
                raise ValueError("Checker candidate validation failed after copy: " + "; ".join(copied_validation.errors))
            manifest["checker_attempted"] = True
            summary.checker_attempted = True
            self._phase(manifest, "checker_started")
            result = self.checker.run(correction=paths.root.parent / "correction" / "correction.yaml", paths=paths)
            manifest["checker"] = _metadata(result)
            summary.checker_duration_seconds = result.duration_seconds
            if result.return_code != 0:
                raise ValueError(f"kathara-lab-checker exited with technical return code {result.return_code}")
            metrics = parse_checker_results(paths)
            manifest["checker_completed"] = True
            summary.checker_completed = True
            manifest["metrics"] = metrics.to_dict()
            summary.total_tests = metrics.total_tests
            summary.passed_tests = metrics.passed_tests
            summary.failed_tests = metrics.failed_tests
            summary.pass_percentage = metrics.pass_percentage
            summary.status = JobStatus.PASSED if metrics.failed_tests == 0 else JobStatus.FAILED
            manifest["status"] = summary.status.value
            self._phase(manifest, "checker_completed")
            self._phase(manifest, summary.status.value)
        except Exception as exc:
            manifest["errors"].append(str(exc))
            manifest["status"] = JobStatus.ERROR.value
            summary.status = JobStatus.ERROR
            summary.error_message = str(exc)
            self._phase(manifest, "error")
        self._write_variant(paths.manifest, manifest)
        return summary

    def process_prompt(self, prompt: PromptRecord, resources: ResourceFiles) -> ExperimentSummary:
        paths = build_experiment_paths(self.config.paths.output, prompt.experiment_id)
        identity = self._identity(prompt, resources)
        skipped = self._can_skip(paths, identity)
        if skipped is not None:
            return skipped
        self._reset_experiment(paths)
        paths.prompt.write_text(prompt.content or "", encoding="utf-8")
        experiment_manifest = {
            "pipeline_version": PIPELINE_VERSION,
            "experiment_id": prompt.experiment_id,
            "prompt_file": prompt.name,
            "prompt_sha256": prompt.prompt_hash,
            "identity": identity,
            "evaluation_spec_generated": False,
            "canonical_correction_sha256": None,
            "complete": False,
            "started_at": _utc_now(),
        }
        write_json_atomic(paths.experiment_manifest, experiment_manifest)

        # Deliberately sequential. Variant B is not started until Variant A generation ended.
        with_summary, with_manifest = self._generate_variant(prompt, Variant.WITH_SKILL, paths.with_skill, resources)
        without_summary, without_manifest = self._generate_variant(prompt, Variant.WITHOUT_SKILL, paths.without_skill, resources)

        evaluation_spec_generated = False
        evaluation_spec_error: str | None = None
        try:
            eval_result = self.evaluation_spec_generator.generate(
                paths=paths,
                prompt_text=prompt.content or "",
                resources=resources,
            )
            evaluation_spec_generated = True
            experiment_manifest["evaluation_spec_generated"] = True
            experiment_manifest["evaluation_spec_generation"] = _metadata(eval_result)
        except Exception as exc:
            evaluation_spec_error = str(exc)
            experiment_manifest["evaluation_spec_error"] = evaluation_spec_error

        correction_hash: str | None = None
        correction_error: str | None = None
        if evaluation_spec_generated:
            try:
                result = self.correction_generator.generate_with_retry(
                    paths=paths,
                    prompt_text=prompt.content or "",
                    resources=resources,
                    validator=CorrectionValidator(resources.checker_schema),
                )
                correction_hash = sha256_file(paths.correction)
                experiment_manifest["canonical_correction_sha256"] = correction_hash
                experiment_manifest["correction_generation"] = _metadata(result)
            except Exception as exc:
                correction_error = str(exc)
                experiment_manifest["correction_error"] = correction_error

        if correction_hash is not None:
            with_summary = self._evaluate_variant(prompt, paths.with_skill, with_summary, with_manifest, correction_hash)
            without_summary = self._evaluate_variant(prompt, paths.without_skill, without_summary, without_manifest, correction_hash)
        else:
            for summary, manifest, variant_paths in (
                (with_summary, with_manifest, paths.with_skill),
                (without_summary, without_manifest, paths.without_skill),
            ):
                if summary.static_validation_passed:
                    summary.status = JobStatus.ERROR
                    if not evaluation_spec_generated:
                        summary.error_message = f"Evaluation spec generation failed: {evaluation_spec_error}"
                    else:
                        summary.error_message = f"Canonical correction unavailable: {correction_error}"
                    manifest["errors"].append(summary.error_message)
                    manifest["status"] = JobStatus.ERROR.value
                    self._phase(manifest, "error")
                    self._write_variant(variant_paths.manifest, manifest)

        outcome, reason = compare_variants(with_summary, without_summary)
        experiment = ExperimentSummary(
            prompt.experiment_id,
            prompt.name,
            evaluation_spec_generated,
            correction_hash is not None,
            correction_hash,
            with_summary,
            without_summary,
            outcome,
            reason,
        )
        write_comparison(experiment, paths.comparison, paths.comparison_csv)
        experiment_manifest.update({
            "canonical_correction_sha256": correction_hash,
            "comparison": outcome.value,
            "comparison_reason": reason,
            "complete": True,
            "finished_at": _utc_now(),
        })
        write_json_atomic(paths.experiment_manifest, experiment_manifest)

        if not self.config.processing.keep_workspaces:
            workspace_root = paths.root / ".workspaces"
            if workspace_root.exists():
                shutil.rmtree(workspace_root)
        return experiment

    def dry_run(self, prompts: list[PromptRecord], prompts_dir: Path, resources: ResourceFiles, *, verbose: bool = False) -> None:
        print("Dry-run framework")
        print(f"Prompt directory: {Path(prompts_dir).resolve(strict=False)}")
        print(f"Prompt trovati: {len(prompts)}")
        print(f"Provider: {self.config.generation.provider}")
        if self.config.generation.model:
            print(f"Model: {self.config.generation.model}")
        if self.config.generation.reasoning_effort:
            print(f"Reasoning: {self.config.generation.reasoning_effort}")
        print("Ordine per prompt: with_skill -> without_skill -> canonical correction -> checker with_skill -> checker without_skill -> comparison")
        print("Prompt selezionati:")
        for index, prompt in enumerate(prompts, 1):
            print(f"  {index}. {prompt.name}")
            if verbose:
                paths = build_experiment_paths(self.config.paths.output, prompt.experiment_id)
                for variant, variant_paths in ((Variant.WITH_SKILL, paths.with_skill), (Variant.WITHOUT_SKILL, paths.without_skill)):
                    command = self.runner.build_command(
                        instruction=self.lab_generator.instruction(variant),
                        workspace=variant_paths.workspace,
                        output_last_message=variant_paths.workspace / ".agent-last-message.txt",
                    )
                    print(f"     {variant.value} workspace: {variant_paths.workspace}")
                    print(f"     {variant.value} argv: {list(command)}")
                corr_cmd = self.runner.build_command(
                    instruction=self.correction_generator.instruction(),
                    workspace=paths.correction_workspace,
                    output_last_message=paths.correction_workspace / ".agent-last-message.txt",
                )
                print(f"     correction argv: {list(corr_cmd)}")
                print(f"     correction shared: {paths.correction}")
                print(f"     checker with_skill: {list(self.checker.build_command(correction=paths.correction, paths=paths.with_skill))}")
                print(f"     checker without_skill: {list(self.checker.build_command(correction=paths.correction, paths=paths.without_skill))}")
        print("Nessuna operazione eseguita.")

    def run(self, prompts: list[PromptRecord], resources: ResourceFiles) -> PipelineSummary:
        ensure_output_root(self.config.paths.output, initialize=True)
        started_mono = time.monotonic()
        started_at = _utc_now()
        experiments: list[ExperimentSummary] = []
        for prompt in prompts:
            try:
                experiments.append(self.process_prompt(prompt, resources))
            except Exception as exc:
                # Catastrophic pair-level failure: preserve execution of later prompts when configured.
                a = VariantSummary(prompt.experiment_id, prompt.name, Variant.WITH_SKILL, JobStatus.ERROR, error_message=str(exc))
                b = VariantSummary(prompt.experiment_id, prompt.name, Variant.WITHOUT_SKILL, JobStatus.ERROR, error_message=str(exc))
                experiments.append(ExperimentSummary(prompt.experiment_id, prompt.name, False, None, a, b, ComparisonOutcome.INCOMPARABLE, str(exc)))
                if not self.config.processing.continue_on_error:
                    break
        aggregate = write_aggregate(self.config.paths.output, experiments)
        variant_counts: dict[str, dict[str, int]] = {}
        for name, getter in (("with_skill", lambda e: e.with_skill), ("without_skill", lambda e: e.without_skill)):
            items = [getter(item) for item in experiments]
            variant_counts[name] = {status.value: sum(1 for item in items if item.status is status) for status in (JobStatus.PASSED, JobStatus.FAILED, JobStatus.ERROR, JobStatus.SKIPPED)}
        comparisons = {outcome.value: sum(1 for item in experiments if item.comparison is outcome) for outcome in ComparisonOutcome}
        summary = PipelineSummary(
            pipeline_version=PIPELINE_VERSION,
            started_at=started_at,
            finished_at=_utc_now(),
            duration_seconds=time.monotonic() - started_mono,
            prompts_found=len(prompts),
            experiments_completed=len(experiments),
            variant_counts=variant_counts,
            comparisons=comparisons,
            experiments=experiments,
        )
        write_json_atomic(self.config.paths.output / "pipeline-summary.json", summary.to_dict())
        return summary
