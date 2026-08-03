from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class PipelineError(Exception):
    """Base error for the application."""


class ConfigurationError(PipelineError):
    """The pipeline configuration is invalid."""


class PreflightError(PipelineError):
    """A mandatory environment check failed."""

    def __init__(self, message: str, details: Sequence[str] | None = None) -> None:
        super().__init__(message)
        self.details = tuple(details or ())


class PromptDiscoveryError(PipelineError):
    """Prompt discovery could not be completed."""


class PipelineJobError(PipelineError):
    """Base error scoped to one prompt job."""

    def __init__(
        self,
        message: str,
        details: Sequence[str] | None = None,
        *,
        process_metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.details = tuple(details or ())
        # Keep the existing two-argument constructor valid while allowing the
        # process runners to preserve the evidence needed to diagnose a failed
        # external invocation.  A copy avoids a later caller mutation changing
        # the exception after it was raised.
        self.process_metadata = dict(process_metadata) if process_metadata is not None else None


class CodexExecutionError(PipelineJobError):
    """Codex did not complete successfully."""


class CodexAuthenticationError(CodexExecutionError):
    """Codex could not authenticate the non-interactive execution."""


class CodexSignalError(CodexExecutionError):
    """The Codex process was terminated by an operating-system signal."""


class LabGenerationError(PipelineJobError):
    """A generated lab could not be collected."""


class LabValidationError(PipelineJobError):
    """Static lab validation failed."""


class CorrectionGenerationError(PipelineJobError):
    """The correction file could not be generated."""


class YamlValidationError(PipelineJobError):
    """The correction file is not valid YAML."""


class SchemaValidationError(PipelineJobError):
    """The correction file does not match its schema."""


class SemanticValidationError(PipelineJobError):
    """The correction file is inconsistent with its lab."""


class CheckerExecutionError(PipelineJobError):
    """The checker process did not complete successfully."""


class ReportParsingError(PipelineJobError):
    """Checker reports are missing or cannot be interpreted."""


class UnsafePathError(PipelineError):
    """A filesystem operation targeted an unsafe path."""


class ManifestError(PipelineJobError):
    """A job manifest could not be read or written."""
