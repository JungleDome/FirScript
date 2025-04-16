"""Runtime-related exceptions for the script engine."""
from .base import ScriptEngineError

class ScriptRuntimeError(ScriptEngineError):
    """Raised when script execution fails."""
    def __init__(self, message, file=None, line=None, col=None):
        super().__init__(message)
        self.file = file
        self.line = line
        self.col = col
        
class ScriptCompilationError(ScriptRuntimeError):
    """Raised when script compilation fails."""
    pass

class ScriptNotFoundError(ScriptRuntimeError):
    """Raised when a script definition cannot be found."""
    pass

class EntrypointNotFoundError(ScriptRuntimeError):
    """Raised when an entrypoint script cannot be found."""
    pass