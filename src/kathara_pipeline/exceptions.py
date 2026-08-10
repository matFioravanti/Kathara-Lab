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


class GenerationError(KatharaFrameworkError):
    def __init__(self, message: str, result: 'GenerationResult'):
        super().__init__(message)
        self.result = result



class ValidationError(KatharaFrameworkError):
    pass


class CheckerExecutionError(KatharaFrameworkError):
    pass


class ReportParsingError(KatharaFrameworkError):
    pass
