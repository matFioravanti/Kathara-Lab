from __future__ import annotations


class KatharaFrameworkError(Exception):
    """Base framework exception."""


class ConfigurationError(KatharaFrameworkError):
    pass


class PromptDiscoveryError(KatharaFrameworkError):
    pass


class ResourceError(KatharaFrameworkError):
    pass


class UnsafePathError(KatharaFrameworkError):
    pass


class AgentExecutionError(KatharaFrameworkError):
    pass


class ValidationError(KatharaFrameworkError):
    pass


class CheckerExecutionError(KatharaFrameworkError):
    pass


class ReportParsingError(KatharaFrameworkError):
    pass
