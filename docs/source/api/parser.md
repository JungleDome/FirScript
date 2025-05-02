# Parser API

The `ScriptParser` class is responsible for parsing script source code, determining script types, extracting metadata, and validating script constraints in FirScript.

## Class: ScriptParser

```python
class ScriptParser:
    def __init__(self):
        ...
```

The `ScriptParser` parses and validates script source code, extracting metadata and determining script types.

### Methods

#### parse(source, script_id, script_type)

```python
def parse(self, source: str, script_id: str, script_type: ScriptType = None) -> Script:
    ...
```

Parses and validates a script source.

**Parameters**:
- **source** (`str`): The script source code to parse
- **script_id** (`str`): An identifier for the script (usually a name or path)
- **script_type** (`ScriptType`, optional): The type of script to parse. If not provided, the parser will attempt to determine the type automatically.

**Returns**:
- A `Script` object containing the parsed script and its metadata

**Raises**:
- `ScriptParsingError`: If the script has syntax errors
- `MissingScriptTypeError`: If the script type cannot be determined
- `ConflictingScriptTypeError`: If the script has conflicting characteristics
- `MissingRequiredFunctionsError`: If a strategy or indicator script is missing required functions
- `NoExportsError`: If a library script doesn't export anything
- `MultipleExportsError`: If a script has multiple export statements
- `InvalidInputUsageError`: If input functions are used outside of setup()
- `StrategyGlobalVariableError`: If variables are assigned at the global scope
- `ReservedVariableNameError`: If reserved variable names are used

**Example**:
```python
from firscript import ScriptParser, ScriptType

# Create a parser
parser = ScriptParser()

# Parse a script
script_source = """
def setup():
    global length
    length = input.int('Length', 14)

def process():
    sma_value = ta.sma(data.all.close, length)[-1]
    chart.plot(sma_value, title="SMA")
"""

# Parse the script as an indicator
script = parser.parse(script_source, script_id="my_indicator", script_type=ScriptType.INDICATOR)

# Access script metadata
print(f"Script type: {script.metadata.type}")
print(f"Script exports: {script.metadata.exports}")
```

### Internal Methods

The following methods are used internally by the parser and are not typically called directly:

#### _determine_script_type(tree)

```python
def _determine_script_type(self, tree: ast.AST) -> ScriptType:
    ...
```

Determines the script type based on function definitions and exports.

A script is considered a:
- **Strategy**: If it contains both setup() and process() functions and uses the strategy namespace
- **Indicator**: If it contains both setup() and process() functions but doesn't use the strategy namespace
- **Library**: If it has an export variable but no setup/process functions

**Parameters**:
- **tree** (`ast.AST`): The AST (Abstract Syntax Tree) of the parsed script

**Returns**:
- The determined `ScriptType`

**Raises**:
- `ConflictingScriptTypeError`: If script has conflicting characteristics
- `MissingScriptTypeError`: If script doesn't match any type criteria

#### _extract_metadata(tree, script_type, script_id)

```python
def _extract_metadata(self, tree: ast.AST, script_type: ScriptType, script_id: str) -> ScriptMetadata:
    ...
```

Extracts metadata from the script.

**Parameters**:
- **tree** (`ast.AST`): The AST of the parsed script
- **script_type** (`ScriptType`): The type of the script
- **script_id** (`str`): The identifier for the script

**Returns**:
- A `ScriptMetadata` object containing the extracted metadata

#### _validate_script(tree, metadata)

```python
def _validate_script(self, tree: ast.AST, metadata: ScriptMetadata) -> None:
    ...
```

Validates that the script adheres to the constraints of its type.

**Parameters**:
- **tree** (`ast.AST`): The AST of the parsed script
- **metadata** (`ScriptMetadata`): The metadata extracted from the script

**Raises**:
- `MissingRequiredFunctionsError`: If a strategy or indicator script is missing required functions
- `NoExportsError`: If a library script doesn't export anything
- `InvalidInputUsageError`: If input functions are used outside of setup()
- `StrategyGlobalVariableError`: If variables are assigned at the global scope
- `StrategyFunctionInIndicatorError`: If strategy functions are used in a library script

#### _is_reserved_variable_name(var_name)

```python
def _is_reserved_variable_name(self, var_name: str) -> bool:
    ...
```

Checks if a variable name matches the reserved pattern (`__name__`).

**Parameters**:
- **var_name** (`str`): The variable name to check

**Returns**:
- `True` if the variable name is reserved, `False` otherwise

#### _create_script(source, metadata)

```python
def _create_script(self, source: str, metadata: ScriptMetadata) -> Script:
    ...
```

Creates a script instance with source and metadata.

**Parameters**:
- **source** (`str`): The script source code
- **metadata** (`ScriptMetadata`): The metadata extracted from the script

**Returns**:
- A `Script` object containing the source and metadata

## Script Validation Rules

The parser enforces several validation rules for scripts:

1. **Script Type Constraints**:
   - Strategy and indicator scripts must have both `setup()` and `process()` functions
   - Library scripts must have an `export` variable and cannot have `setup()` or `process()` functions

2. **Variable Scope**:
   - Variables should not be assigned at the global scope
   - All variable declarations should be inside `setup()` or `process()` functions

3. **Input Usage**:
   - Input functions (`input.int()`, `input.float()`, etc.) can only be used in the `setup()` function

4. **Reserved Variable Names**:
   - Variable names matching the pattern `__name__` (double underscores at both start and end) are reserved for system use
   - Scripts cannot export variables with this naming pattern

5. **Namespace Usage**:
   - Library scripts cannot use the strategy namespace

## Example: Parsing Different Script Types

### Strategy Script

```python
from firscript import ScriptParser

parser = ScriptParser()

strategy_source = """
def setup():
    global fast_length, slow_length
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)

def process():
    global fast_length, slow_length
    
    # Calculate moving averages
    fast_ma = ta.sma(data.all.close, fast_length)[-1]
    slow_ma = ta.sma(data.all.close, slow_length)[-1]
    
    # Trading logic
    if fast_ma > slow_ma:
        strategy.long()
    elif fast_ma < slow_ma:
        strategy.short()
"""

strategy_script = parser.parse(strategy_source, script_id="my_strategy")
print(f"Script type: {strategy_script.metadata.type}")  # Output: Script type: ScriptType.STRATEGY
```

### Indicator Script

```python
from firscript import ScriptParser

parser = ScriptParser()

indicator_source = """
def setup():
    global length
    length = input.int('Length', 14)

def process():
    # Calculate RSI
    rsi_value = ta.rsi(data.all.close, length)[-1]
    
    # Plot the indicator
    chart.plot(rsi_value, title="RSI")
"""

indicator_script = parser.parse(indicator_source, script_id="my_indicator")
print(f"Script type: {indicator_script.metadata.type}")  # Output: Script type: ScriptType.INDICATOR
```

### Library Script

```python
from firscript import ScriptParser

parser = ScriptParser()

library_source = """
def calculate_momentum(values, period=14):
    """Calculate momentum: current value - value 'period' bars ago"""
    if len(values) < period:
        return 0
    return values[-1] - values[-period]

def calculate_rate_of_change(values, period=14):
    """Calculate rate of change: (current value / value 'period' bars ago - 1) * 100"""
    if len(values) < period or values[-period] == 0:
        return 0
    return (values[-1] / values[-period] - 1) * 100

# Export the functions as a dictionary
export = {
    "momentum": calculate_momentum,
    "roc": calculate_rate_of_change
}
"""

library_script = parser.parse(library_source, script_id="my_library")
print(f"Script type: {library_script.metadata.type}")  # Output: Script type: ScriptType.LIBRARY
print(f"Script exports: {library_script.metadata.exports}")  # Output: Script exports: {'export'}
```
