# Exceptions API

FirScript provides a comprehensive set of exceptions to handle various error conditions that may occur during script parsing, validation, and execution.

## Base Exception

### ScriptEngineError

```python
class ScriptEngineError(Exception):
    """Base class for all script engine exceptions."""
    pass
```

The base class for all script engine exceptions. All other exceptions in FirScript inherit from this class.

## Parsing Exceptions

These exceptions are raised during script parsing and validation.

### ScriptParsingError

```python
class ScriptParsingError(ScriptEngineError):
    """Raised when script parsing fails."""
    def __init__(self, message, file=None, line=None, col=None):
        ...
```

Base class for parsing-related exceptions.

**Attributes**:
- **message** (`str`): The error message
- **file** (`str`, optional): The file where the error occurred
- **line** (`int`, optional): The line number where the error occurred
- **col** (`int`, optional): The column number where the error occurred

### CircularImportError

```python
class CircularImportError(ScriptParsingError):
    """Raised when circular imports are detected."""
    pass
```

Raised when a circular import is detected. For example, if script A imports script B, and script B imports script A.

### InvalidInputUsageError

```python
class InvalidInputUsageError(ScriptParsingError):
    """Raised when input.* is used incorrectly."""
    pass
```

Raised when input functions are used incorrectly, such as using `input.int()` in the `process()` function.

### ReservedVariableNameError

```python
class ReservedVariableNameError(ScriptParsingError):
    """Raised when a reserved variable name is used."""
    pass
```

Raised when a script uses a reserved variable name, such as a name with double underscores at both ends (`__name__`).

### ScriptValidationError

```python
class ScriptValidationError(ScriptParsingError):
    """Raised when script validation fails."""
    pass
```

Base class for validation-related exceptions.

### ConflictingScriptTypeError

```python
class ConflictingScriptTypeError(ScriptValidationError):
    """Raised when a script is both a strategy and an indicator."""
    pass
```

Raised when a script has conflicting characteristics, such as having both strategy and library features.

### MissingScriptTypeError

```python
class MissingScriptTypeError(ScriptValidationError):
    """Raised when a script is neither a strategy nor an indicator."""
    pass
```

Raised when a script doesn't match any of the supported script types (strategy, indicator, or library).

### MissingRequiredFunctionsError

```python
class MissingRequiredFunctionsError(ScriptValidationError):
    """Raised when a strategy script is missing required functions."""
    pass
```

Raised when a strategy or indicator script is missing required functions, such as `setup()` or `process()`.

### MultipleExportsError

```python
class MultipleExportsError(ScriptValidationError):
    """Raised when an indicator script has multiple exports."""
    pass
```

Raised when a script has multiple export statements.

### StrategyFunctionInIndicatorError

```python
class StrategyFunctionInIndicatorError(ScriptValidationError):
    """Raised when an indicator script uses strategy functions."""
    pass
```

Raised when a library script uses strategy functions.

### StrategyGlobalVariableError

```python
class StrategyGlobalVariableError(ScriptValidationError):
    """Raised when a strategy script uses global variables."""
    pass
```

Raised when a script assigns variables at the global scope, outside of functions.

### NoExportsError

```python
class NoExportsError(ScriptValidationError):
    """Raised when a library script doesn't export anything."""
    pass
```

Raised when a library script doesn't export anything.

## Runtime Exceptions

These exceptions are raised during script execution.

### ScriptRuntimeError

```python
class ScriptRuntimeError(ScriptEngineError):
    """Raised when script execution fails."""
    def __init__(self, message, file=None, name=None, line_no=None, line_str=None, col_no=None, exception_msg=None):
        ...
```

Base class for runtime-related exceptions.

**Attributes**:
- **message** (`str`): The error message
- **file** (`str`, optional): The file where the error occurred
- **name** (`str`, optional): The name of the script
- **line_no** (`int`, optional): The line number where the error occurred
- **line_str** (`str`, optional): The line of code that caused the error
- **col_no** (`int`, optional): The column number where the error occurred
- **exception_msg** (`str`, optional): The original exception message

### ScriptCompilationError

```python
class ScriptCompilationError(ScriptRuntimeError):
    """Raised when script compilation fails."""
    pass
```

Raised when a script fails to compile.

### ScriptNotFoundError

```python
class ScriptNotFoundError(ScriptRuntimeError):
    """Raised when a script definition cannot be found."""
    pass
```

Raised when a script tries to import a script that doesn't exist.

### EntrypointNotFoundError

```python
class EntrypointNotFoundError(ScriptRuntimeError):
    """Raised when an entrypoint script cannot be found."""
    pass
```

Raised when no main script has been provided to the importer.

## Exception Handling

When working with FirScript, it's important to handle exceptions appropriately. Here's an example of how to handle exceptions:

```python
from firscript import Engine
from firscript.exceptions import ScriptEngineError, ScriptParsingError, ScriptRuntimeError

try:
    # Create an engine
    engine = Engine(data, main_script_str=script_source)
    
    # Run the script
    results = engine.run()
    
    # Process the results
    print(results)
except ScriptParsingError as e:
    print(f"Parsing error: {e}")
    if e.file:
        print(f"File: {e.file}")
    if e.line:
        print(f"Line: {e.line}")
except ScriptRuntimeError as e:
    print(f"Runtime error: {e}")
    if e.file:
        print(f"File: {e.file}")
    if e.line_no:
        print(f"Line: {e.line_no}")
    if e.line_str:
        print(f"Code: {e.line_str}")
except ScriptEngineError as e:
    print(f"Script engine error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Common Error Scenarios

Here are some common error scenarios and the exceptions they raise:

### Syntax Errors

```python
# Syntax error in script
script_source = """
def setup():
    global length
    length = input.int('Length', 14

def process():
    pass
"""

# Raises ScriptParsingError
```

### Missing Required Functions

```python
# Missing process() function
script_source = """
def setup():
    global length
    length = input.int('Length', 14)
"""

# Raises MissingRequiredFunctionsError
```

### Input Usage in Process

```python
# Using input in process()
script_source = """
def setup():
    pass

def process():
    length = input.int('Length', 14)
"""

# Raises InvalidInputUsageError
```

### Global Variable Assignment

```python
# Assigning variables at global scope
script_source = """
length = 14

def setup():
    pass

def process():
    pass
"""

# Raises StrategyGlobalVariableError
```

### Circular Imports

```python
# Script A imports Script B, which imports Script A
script_a = """
def setup():
    global lib
    lib = import_script('script_b')

def process():
    pass
"""

script_b = """
def setup():
    global lib
    lib = import_script('script_a')

def process():
    pass
"""

# Raises CircularImportError
```

### Script Not Found

```python
# Importing a non-existent script
script_source = """
def setup():
    global lib
    lib = import_script('non_existent_script')

def process():
    pass
"""

# Raises ScriptNotFoundError
```

### Runtime Errors

```python
# Division by zero
script_source = """
def setup():
    pass

def process():
    result = 1 / 0
"""

# Raises ScriptRuntimeError
```
