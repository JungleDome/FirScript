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

class ConflictingScriptTypeError(ScriptValidationError):
    """Raised when a script is both a strategy and an indicator."""
    pass

class MissingScriptTypeError(ScriptValidationError):
    """Raised when a script is neither a strategy nor an indicator."""
    pass

class MissingRequiredFunctionsError(ScriptValidationError):
    """Raised when a strategy script is missing required functions."""
    pass

class MultipleExportsError(ScriptValidationError):
    """Raised when an indicator script has multiple exports."""
    pass

class StrategyFunctionInIndicatorError(ScriptValidationError):
    """Raised when an indicator script uses strategy functions."""
    pass

class StrategyGlobalVariableError(ScriptValidationError):
    """Raised when a strategy script uses global variables."""
    pass

class ReservedVariableNameError(ScriptValidationError):
    """Raised when a script uses a reserved variable name format (__name__)."""
    pass