from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .console import PipelineConsole
from .correction_validator import CorrectionValidator
from .exceptions import KatharaFrameworkError
from .lab_validator import LabValidator
from .models import ComparisonOutcome, ExperimentSummary, JobStatus, Variant, VariantSummary
from .pipeline import PIPELINE_VERSION, Pipeline
from .report_aggregator import write_aggregate
from .state_store import read_json

EXIT_SUCCESS = 0
EXIT_FAILED = 1
EXIT_ERROR = 2
EXIT_PREFLIGHT = 3


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kathara-experiment",
        description="Paired LLM experiment framework for Kathara labs: with creation Skill vs without Skill.",
    )
    parser.add_argument("--config", default="pipeline.yaml", help="Path to pipeline.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run paired experiments for prompts in an external directory")
    run.add_argument("--prompts-dir", required=True, type=Path)
    run.add_argument("--output-dir", type=Path)
    run.add_argument("--prompt", help="Process only this prompt filename")
    run.add_argument("--all", action="store_true", help="Compatibility flag; all prompts are the default")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--verbose", action="store_true")
    run.add_argument("--force", action="store_true")
    run.add_argument("--resume-from", choices=["correction"], help="Resume pipeline from a specific phase")

    pre = sub.add_parser("preflight", help="Validate inputs/resources/tool availability")
    pre.add_argument("--prompts-dir", required=True, type=Path)
    pre.add_argument("--output-dir", type=Path)
    pre.add_argument("--dry-run", action="store_true", help="Report missing external tools as warnings")

    status = sub.add_parser("status", help="Read persisted experiment state")
    status.add_argument("--output-dir", type=Path)

    compare = sub.add_parser("compare", help="Rebuild aggregate reports from persisted pair results")
    compare.add_argument("--output-dir", type=Path)

    validate = sub.add_parser("validate", help="Statically validate persisted artifacts without running agents/checker")
    validate.add_argument("--output-dir", type=Path)

    return parser


def _select(prompts, filename: str | None):
    if filename is None:
        return prompts
    selected = [item for item in prompts if item.name == filename]
    if not selected:
        raise KatharaFrameworkError(f"Prompt non trovato nella directory indicata: {filename}")
    return selected


def _exit_for_summary(summary) -> int:
    if any(
        item.status is JobStatus.ERROR
        for exp in summary.experiments
        for item in (exp.with_skill, exp.without_skill)
    ):
        return EXIT_ERROR
    if any(
        item.status is JobStatus.FAILED
        for exp in summary.experiments
        for item in (exp.with_skill, exp.without_skill)
    ):
        return EXIT_FAILED
    return EXIT_SUCCESS


def _print_summary(summary) -> None:
    print("Riepilogo esperimento:")
    print(f"  Prompt: {summary.prompts_found}")
    for variant in ("with_skill", "without_skill"):
        counts = summary.variant_counts.get(variant, {})
        print(
            f"  {variant}: passed={counts.get('passed', 0)} failed={counts.get('failed', 0)} "
            f"error={counts.get('error', 0)} skipped={counts.get('skipped', 0)}"
        )
    print("  Confronti:")
    for outcome, value in summary.comparisons.items():
        print(f"    {outcome}: {value}")
    print("Esperimenti:")
    for exp in summary.experiments:
        print(
            f"  {exp.experiment_id}: with_skill={exp.with_skill.status.value}, "
            f"without_skill={exp.without_skill.status.value}, comparison={exp.comparison.value}"
        )


def _variant_from_manifest(data: dict, variant: Variant) -> VariantSummary:
    metrics = data.get("metrics") or {}
    generation = data.get("generation") or {}
    correction_generation = data.get("correction_generation") or {}
    checker = data.get("checker") or {}
    errors = data.get("errors") or []
    return VariantSummary(
        experiment_id=str(data.get("experiment_id", "unknown")),
        prompt_file=str(data.get("prompt_file", "unknown")),
        variant=variant,
        status=JobStatus(str(data.get("status", "error"))) if str(data.get("status", "error")) in {s.value for s in JobStatus} else JobStatus.ERROR,
        evaluation_spec_hash=data.get("evaluation_spec_hash"),
        correction_generated=bool(data.get("correction_generated")),
        correction_hash=data.get("correction_hash"),
        lab_generated=bool(data.get("lab_generated")),
        static_validation_passed=bool(data.get("static_validation_passed")),
        checker_attempted=bool(data.get("checker_attempted")),
        checker_completed=bool(data.get("checker_completed")),
        total_tests=metrics.get("total_tests"),
        passed_tests=metrics.get("passed_tests"),
        failed_tests=metrics.get("failed_tests"),
        pass_percentage=metrics.get("pass_percentage"),
        lab_duration_seconds=generation.get("duration_seconds"),
        correction_duration_seconds=correction_generation.get("duration_seconds"),
        checker_duration_seconds=checker.get("duration_seconds"),
        error_message=str(errors[-1]) if errors else None,
    )


def _load_experiments(output: Path) -> list[ExperimentSummary]:
    result: list[ExperimentSummary] = []
    if not output.is_dir():
        return result
    for root in sorted(output.iterdir(), key=lambda p: p.name.casefold()):
        if not root.is_dir() or root.name.startswith(".") or root.name == "summary":
            continue
        exp = read_json(root / "experiment.json")
        comp = read_json(root / "comparison.json")
        a = read_json(root / "with_skill" / "manifest.json")
        b = read_json(root / "without_skill" / "manifest.json")
        if not exp or not comp or not a or not b:
            continue
        try:
            outcome = ComparisonOutcome(str(comp.get("outcome")))
        except ValueError:
            outcome = ComparisonOutcome.INCOMPARABLE
        result.append(
            ExperimentSummary(
                experiment_id=str(exp.get("experiment_id", root.name)),
                prompt_file=str(exp.get("prompt_file", "prompt.md")),
                evaluation_spec_generated=bool(exp.get("evaluation_spec_generated")),
                with_skill=_variant_from_manifest(a, Variant.WITH_SKILL),
                without_skill=_variant_from_manifest(b, Variant.WITHOUT_SKILL),
                comparison=outcome,
                comparison_reason=comp.get("reason"),
            )
        )
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = load_config(args.config)
        config = config.with_overrides(
            output_dir=getattr(args, "output_dir", None),
            force=getattr(args, "force", None),
            resume_from=getattr(args, "resume_from", None)
        )

        if args.command in {"run", "preflight"}:
            console = PipelineConsole()
            pipeline = Pipeline(config, console=console)
            prompts = _select(pipeline.discover(args.prompts_dir), getattr(args, "prompt", None))
            dry = bool(getattr(args, "dry_run", False))
            preflight = pipeline.preflight(args.prompts_dir, prompts, dry_run=dry)
            for warning in preflight.warnings:
                print(f"AVVISO: {warning}")
            if args.command == "preflight":
                print(f"Preflight completato: {len(prompts)} prompt, risorse valide.")
                return EXIT_SUCCESS
            if dry:
                pipeline.dry_run(prompts, args.prompts_dir, preflight.resources, verbose=args.verbose)
                return EXIT_SUCCESS
                
            if args.command == "run":
                console.pipeline_started(
                    provider=config.generation.provider,
                    model=config.generation.model,
                    reasoning=config.generation.reasoning_effort,
                    prompts_count=len(prompts)
                )
            summary = pipeline.run(prompts, preflight.resources)
            return _exit_for_summary(summary)

        output = config.paths.output
        if args.command == "status":
            persisted = read_json(output / "pipeline-summary.json")
            experiments = _load_experiments(output)
            if not persisted and not experiments:
                print("Nessuna esecuzione registrata.")
                return EXIT_SUCCESS
            if persisted:
                print(f"Pipeline version: {persisted.get('pipeline_version', '?')}")
                print(f"Prompt: {persisted.get('prompts_found', len(experiments))}")
            for exp in experiments:
                print(
                    f"{exp.experiment_id}: with_skill={exp.with_skill.status.value}, "
                    f"without_skill={exp.without_skill.status.value}, comparison={exp.comparison.value}"
                )
            if any(v.status is JobStatus.ERROR for e in experiments for v in (e.with_skill, e.without_skill)):
                return EXIT_ERROR
            if any(v.status is JobStatus.FAILED for e in experiments for v in (e.with_skill, e.without_skill)):
                return EXIT_FAILED
            return EXIT_SUCCESS

        if args.command == "compare":
            experiments = _load_experiments(output)
            if not experiments:
                raise KatharaFrameworkError(f"Nessuna coppia persistita trovata in {output}")
            write_aggregate(output, experiments)
            print(f"Report aggregati rigenerati per {len(experiments)} coppie in {output / 'summary'}")
            return EXIT_SUCCESS

        if args.command == "validate":
            lab_validator = LabValidator()
            correction_validator = CorrectionValidator()
            invalid = 0
            checked = 0
            for root in sorted(output.iterdir()) if output.is_dir() else []:
                if not root.is_dir() or root.name.startswith(".") or root.name == "summary":
                    continue
                prompt = root / "prompt.md"
                text = prompt.read_text(encoding="utf-8") if prompt.is_file() else ""
                for name in ("with_skill", "without_skill"):
                    correction = root / name / "correction" / "correction.yaml"
                    if correction.is_file():
                        checked += 1
                        result = correction_validator.validate(correction)
                        if not result.valid:
                            invalid += 1
                            print(f"{root.name}/{name}/correction: ERROR: {'; '.join(result.errors)}")
                    source = root / name / "source"
                    if source.is_dir():
                        checked += 1
                        result = lab_validator.validate(source, text)
                        if not result.valid:
                            invalid += 1
                            print(f"{root.name}/{name}: ERROR: {'; '.join(result.errors)}")
            print(f"Artefatti controllati: {checked}; invalidi: {invalid}")
            return EXIT_ERROR if invalid else EXIT_SUCCESS

        raise KatharaFrameworkError("Comando non gestito")
    except KatharaFrameworkError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return EXIT_PREFLIGHT if args.command in {"run", "preflight"} else EXIT_ERROR
    except Exception as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
