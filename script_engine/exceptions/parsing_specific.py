"""Specific parsing-related exceptions for the script engine."""
from .parsing import ScriptParsingError

class CircularImportError(ScriptParsingError):
    """Raised when circular imports are detected."""
    pass

class InvalidInputUsageError(ScriptParsingError):
    """Raised when input.* is used incorrectly."""
    pass

class ScriptValidationError(ScriptParsingError):
    """Raised when script validation fails."""
    pass