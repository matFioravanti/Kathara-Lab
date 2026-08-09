from __future__ import annotations

import sys
from typing import TextIO

class PipelineConsole:
    def __init__(self, stream: TextIO = sys.stdout):
        self._stream = stream

    def _print(self, msg: str = "") -> None:
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
        self._print("        ✓ Checker avviato")

    def checker_completed(self) -> None:
        self._print("        ✓ Checker completato")

    def checker_failed(self, error: str) -> None:
        self._print("        ✗ Checker non completato")
        self._print(f"          Error: {error}")

    def checker_metrics(self, total: int, passed: int, failed: int, pass_percentage: float) -> None:
        self._print(f"        Test: {total} | Passed: {passed} | Failed: {failed} | Pass: {pass_percentage:.2f}%")

    def experiment_result(self, comparison: str, status: str) -> None:
        self._print()
        self._print(f"  Comparison: {comparison}")
        self._print(f"  Risultato esperimento: {status}")
