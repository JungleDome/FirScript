"""Parsing-related exceptions for the script engine."""
from .base import ScriptEngineError

class ScriptParsingError(ScriptEngineError):
    """Raised when script parsing fails."""
    def __init__(self, message, file=None, line=None, col=None):
        super().__init__(message)
        self.file = file
        self.line = line
        self.col = col