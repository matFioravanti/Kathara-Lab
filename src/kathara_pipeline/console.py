from __future__ import annotations

import sys
import threading
from typing import TextIO

def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m = int(seconds // 60)
    s = int(seconds % 60)
    if m < 60:
        return f"{m}m {s}s"
    h = m // 60
    m = m % 60
    return f"{h}h {m}m {s}s"


class PipelineConsole:
    def __init__(self, stream: TextIO = sys.stdout):
        self._stream = stream
        self._lock = threading.Lock()

    def _print(self, msg: str = "") -> None:
        with self._lock:
            print(msg, file=self._stream)

    def pipeline_started(self, provider: str, model: str | None, reasoning: str | None, prompts_count: int) -> None:
        self._print("Kathara-Lab Pipeline")
        self._print("────────────────────────────────────────")
        self._print()
        self._print(f"Provider: {provider}")
        if model:
            self._print(f"Model: {model}")
        if reasoning:
            self._print(f"Reasoning: {reasoning}")
        self._print(f"Prompt trovati: {prompts_count}")
        self._print()

    def experiment_started(self, prompt_name: str, current_index: int, total_prompts: int) -> None:
        if current_index > 1:
            self._print()
        self._print(f"[{current_index}/{total_prompts}] {prompt_name}")
        self._print()

    def phase_started(self, phase_name: str, current_phase: int, total_phases: int) -> None:
        if current_phase > 1:
            self._print()
        self._print(f"  [{current_phase}/{total_phases}] {phase_name}...")

    def phase_success(self, message: str) -> None:
        self._print(f"        ✓ {message}")

    def phase_failure(self, message: str, error: str | None = None) -> None:
        self._print(f"        ✗ {message}")
        if error:
            self._print(f"          Error: {error}")

    def checker_started(self) -> None:
        pass # self._print("        ✓ Checker avviato")

    def checker_completed(self) -> None:
        pass # self._print("        ✓ Checker completato")

    def checker_failed(self, variant: str, error: str) -> None:
        self._print(f"        ✗ Checker {variant} fallito: {error}")

    def checker_metrics(self, variant: str, total: int, passed: int, failed: int, pass_percentage: float) -> None:
        self._print(f"        ✓ Checker {variant}: {passed}/{total} passed ({pass_percentage:.2f}%)")

    def experiment_result(self, experiment) -> None:
        self._print()
        self._print("  Results:")
        
        for name, summary in (("with_skill", experiment.with_skill), ("without_skill", experiment.without_skill)):
            self._print(f"    {name}:")
            if summary.checker_completed and summary.total_tests is not None:
                self._print(f"      Tests: {summary.passed_tests}/{summary.total_tests} passed")
                self._print(f"      Failed: {summary.failed_tests}")
                self._print(f"      Score: {summary.pass_percentage:.2f}%")
            else:
                self._print("      Checker not executed")
                self._print(f"      Reason: {summary.error_message or 'Unknown error'}")
            self._print()

        self._print("  Comparison:")
        self._print(f"    Result: {experiment.comparison.value}")
        if experiment.with_skill.checker_completed and experiment.without_skill.checker_completed:
            passed_delta = (experiment.with_skill.passed_tests or 0) - (experiment.without_skill.passed_tests or 0)
            score_delta = (experiment.with_skill.pass_percentage or 0.0) - (experiment.without_skill.pass_percentage or 0.0)
            self._print(f"    Passed delta: {passed_delta:+d}")
            self._print(f"    Score delta: {score_delta:+.2f}%")
        elif experiment.comparison_reason:
            self._print(f"    Reason: {experiment.comparison_reason}")

    def experiment_completed(self, timings: dict[str, float], with_skill_summary, without_skill_summary) -> None:
        self._print()
        self._print("  Timing:")
        self._print(f"    Lab generation:       {format_duration(timings.get('lab_generation_wall_seconds', 0.0))}")
        self._print(f"      with_skill:          {format_duration(with_skill_summary.lab_duration_seconds or 0.0)}")
        self._print(f"      without_skill:       {format_duration(without_skill_summary.lab_duration_seconds or 0.0)}")
        
        self._print(f"    Corrections:          {format_duration(timings.get('corrections_wall_seconds', 0.0))}")
        
        if with_skill_summary.correction_mode == "full_generation":
            fg_dur = with_skill_summary.correction_duration_seconds or 0.0
            ad_dur = without_skill_summary.correction_duration_seconds or 0.0
        else:
            fg_dur = without_skill_summary.correction_duration_seconds or 0.0
            ad_dur = with_skill_summary.correction_duration_seconds or 0.0
            
        self._print(f"      full_generation:     {format_duration(fg_dur)}")
        self._print(f"      adaptation:          {format_duration(ad_dur)}")
        
        self._print(f"    Checkers:             {format_duration(timings.get('checkers_wall_seconds', 0.0))}")
        self._print(f"    Comparison:           {format_duration(timings.get('comparison_seconds', 0.0))}")
        self._print(f"    Pipeline overhead:    {format_duration(timings.get('pipeline_overhead_seconds', 0.0))}")
        self._print(f"    Total:                {format_duration(timings.get('total_wall_seconds', 0.0))}")

