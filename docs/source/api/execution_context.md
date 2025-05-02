# Execution Context API

The `ScriptContext` class is responsible for executing scripts in a controlled environment in FirScript. It manages the compilation, execution, and output generation of scripts.

## Class: ScriptContext

```python
class ScriptContext:
    def __init__(self, script_str: str, namespaces: dict[str, BaseNamespace], name="<script>"):
        ...
```

The `ScriptContext` class provides a controlled execution environment for scripts.

### Parameters

- **script_str** (`str`): The script source code to execute
- **namespaces** (`dict[str, BaseNamespace]`): A dictionary of namespaces to make available to the script
- **name** (`str`, optional): A name for the script, used in error messages. Defaults to "<script>".

### Attributes

- **name** (`str`): The name of the script
- **script_str** (`str`): The script source code
- **namespaces** (`dict[str, BaseNamespace]`): The namespaces available to the script
- **locals** (`dict`): The local variables of the script
- **globals** (`dict`): The global variables of the script

### Methods

#### compile()

```python
def compile(self):
    ...
```

Compiles the script and executes it to define functions and variables.

**Raises**:
- `ScriptCompilationError`: If there is an error compiling the script

#### run_setup()

```python
def run_setup(self):
    ...
```

Runs the script's `setup()` function if it exists.

**Raises**:
- `ScriptRuntimeError`: If there is an error running the setup function

#### run_process()

```python
def run_process(self):
    ...
```

Runs the script's `process()` function if it exists.

**Returns**:
- The return value of the process function, if any

**Raises**:
- `ScriptRuntimeError`: If there is an error running the process function

#### get_export()

```python
def get_export(self):
    ...
```

Gets the script's `export` variable if it exists.

**Returns**:
- The value of the export variable, or None if it doesn't exist
- If the export value is a dictionary, it is converted to a SimpleNamespace for dot notation access

**Raises**:
- `ScriptRuntimeError`: If there is an error accessing the export variable

#### generate_outputs()

```python
def generate_outputs(self) -> Dict[str, Any]:
    ...
```

Generates outputs from all namespaces that support output generation.

**Returns**:
- A dictionary mapping namespace names to their generated outputs

#### generate_metadatas()

```python
def generate_metadatas(self) -> Dict[str, Any]:
    ...
```

Generates metadata from all namespaces that support metadata generation.

**Returns**:
- A dictionary mapping namespace names to their generated metadata

### Internal Methods

#### _prepare_global_context()

```python
def _prepare_global_context(self):
    ...
```

Initializes the execution context with safe builtins and namespaces.

This method:
1. Sets up a restricted set of built-in functions that are safe to use
2. Blocks access to potentially harmful built-ins like `eval`, `exec`, `open`, etc.
3. Injects the namespaces into the global context

## Script Execution Flow

The typical flow of script execution is:

1. **Initialization**: Create a `ScriptContext` with the script source and namespaces
2. **Compilation**: Call `compile()` to compile the script and define functions and variables
3. **Setup**: Call `run_setup()` to run the script's setup function (once at the beginning)
4. **Processing**: Call `run_process()` for each bar in the data
5. **Output Generation**: Call `generate_outputs()` and/or `generate_metadatas()` to get the results

## Example Usage

```python
from firscript import ScriptContext
from firscript.namespace_registry import NamespaceRegistry

# Create a namespace registry
registry = NamespaceRegistry()
registry.register_default_namespaces({})

# Create a script context
script_source = """
def setup():
    global length
    length = input.int('Length', 14)

def process():
    sma_value = ta.sma(data.all.close, length)[-1]
    chart.plot(sma_value, title="SMA")
"""

context = ScriptContext(script_source, registry.build(), name="my_indicator")

# Compile the script
context.compile()

# Run setup
context.run_setup()

# For each bar in the data
for i in range(len(data)):
    current_bar = data.iloc[i]
    historical_bars = data.iloc[:i+1]
    
    # Update data namespace
    context.namespaces.get('data').set_current_bar(current_bar)
    context.namespaces.get('data').set_all_bar(historical_bars)
    
    # Run process
    context.run_process()

# Get outputs
outputs = context.generate_outputs()
metadata = context.generate_metadatas()

print(outputs)
print(metadata)
```

## Error Handling

The `ScriptContext` class provides detailed error information when scripts fail to compile or run:

### ScriptCompilationError

Raised when there is an error compiling the script. Contains:
- The error message
- The script name

### ScriptRuntimeError

Raised when there is an error running the script. Contains:
- The error message
- The script name
- The exception message
- The line number where the error occurred
- The line of code that caused the error
- The column number where the error occurred

## Security Considerations

The `ScriptContext` class implements several security measures:

1. **Restricted Builtins**: Only a limited set of safe built-in functions are available to scripts
2. **Blocked Harmful Functions**: Potentially harmful functions like `eval`, `exec`, `open`, etc. are blocked
3. **Isolated Execution**: Scripts run in an isolated environment with controlled access to the system

These measures help prevent scripts from performing harmful actions or accessing sensitive system resources.

## Integration with Importer

The `ScriptContext` class is used by the `ScriptImporter` to execute imported scripts:

```python
from firscript.importer import ScriptImporter

# Create an importer
importer = ScriptImporter(registry)

# Add scripts
importer.add_script('main', main_script_str, is_main=True)
importer.add_script('indicator', indicator_script_str)

# Build and run the main script
context = importer.build_main_script()
context.run_setup()

# Process data
for i in range(len(data)):
    # Update data namespace
    # Run process
    # ...

# Get results
export = context.get_export()
outputs = context.generate_outputs()
metadata = context.generate_metadatas()
```
