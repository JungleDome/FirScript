"""Runtime-related exceptions for the script engine."""
from .base import ScriptEngineError

class ScriptRuntimeError(ScriptEngineError):
    """Raised when script execution fails."""
    def __init__(self, message, file=None, line=None):
        super().__init__(message)
        self.file = file
        self.line = line

class NamespaceError(ScriptRuntimeError):
    """Raised for namespace-related errors."""
    pass