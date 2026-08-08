from __future__ import annotations

from .agent_runner import AgentRunner
from .claude_runner import ClaudeRunner
from .codex_runner import CodexRunner
from .config import GenerationSettings
from .gemini_runner import GeminiRunner


def build_runner(settings: GenerationSettings) -> AgentRunner:
    if settings.provider == "codex":
        return CodexRunner(settings.command, settings.model, settings.reasoning_effort, settings.sandbox)
    if settings.provider == "gemini":
        return GeminiRunner(settings.command, settings.model, settings.sandbox)
    if settings.provider == "claude":
        return ClaudeRunner(settings.command, settings.model, settings.reasoning_effort)
    raise ValueError(f"Provider non supportato: {settings.provider}")
