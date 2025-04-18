# Importer API

The `ScriptImporter` class is responsible for managing script imports and dependencies in FirScript. It handles script loading, dependency resolution, and circular import detection.

## Class: ScriptImporter

```python
class ScriptImporter:
    def __init__(self, registry: NamespaceRegistry):
        ...
```

The `ScriptImporter` manages script imports and dependencies.

### Parameters

- **registry** (`NamespaceRegistry`): The namespace registry to use for script execution

### Attributes

- **registry** (`NamespaceRegistry`): The namespace registry
- **loaded_scripts** (`dict`): A cache of loaded scripts
- **import_stack** (`list`): A stack of scripts being imported (used for circular import detection)
- **scripts** (`dict[str, Script]`): A dictionary of registered scripts
- **parser** (`ScriptParser`): The script parser
- **main_script** (`Script`): The main script to execute

### Methods

#### add_script(name, script_str, is_main, script)

```python
def add_script(self, name: str = None, script_str: str = None, is_main = False, script: Script = None) -> Script:
    ...
```

Adds a script to the importer.

**Parameters**:
- **name** (`str`, optional): The name of the script
- **script_str** (`str`, optional): The script source code
- **is_main** (`bool`, optional): Whether this is the main script
- **script** (`Script`, optional): A pre-parsed script object

**Returns**:
- The parsed `Script` object

**Raises**:
- `ValueError`: If neither name and script_str nor script is provided

**Example**:
```python
# Add a script by name and source
importer.add_script('my_indicator', indicator_source)

# Add a script as the main script
importer.add_script('main', strategy_source, is_main=True)

# Add a pre-parsed script
importer.add_script(script=my_script)
```

#### build_main_script()

```python
def build_main_script(self) -> ScriptContext:
    ...
```

Builds and returns a script context for the main script.

**Returns**:
- A `ScriptContext` object for the main script

**Raises**:
- `EntrypointNotFoundError`: If no main script has been provided

**Example**:
```python
# Build the main script context
context = importer.build_main_script()

# Run the script
context.compile()
context.run_setup()
```

#### import_script(name)

```python
def import_script(self, name):
    ...
```

Imports a script by name. This method is used by scripts to import other scripts.

**Parameters**:
- **name** (`str`): The name of the script to import

**Returns**:
- The exported value of the script, or the script context if no export is defined

**Raises**:
- `CircularImportError`: If a circular import is detected
- `ScriptNotFoundError`: If the script is not found

**Example**:
```python
# Import a script
lib = import_script('my_library')

# Use the imported script
result = lib.calculate_something(data)
```

## Script Import Flow

The typical flow of script imports is:

1. **Registration**: Scripts are registered with the importer using `add_script()`
2. **Main Script**: One script is designated as the main script
3. **Building**: The main script context is built using `build_main_script()`
4. **Importing**: Scripts can import other scripts using the `import_script` function
5. **Execution**: The main script and its imports are executed

## Circular Import Detection

The `ScriptImporter` detects circular imports by maintaining an import stack. When a script is imported, it is added to the stack. If a script attempts to import a script that is already in the stack, a `CircularImportError` is raised.

## Example Usage

```python
from script_engine import ScriptImporter, NamespaceRegistry

# Create a namespace registry
registry = NamespaceRegistry()
registry.register_default_namespaces({})

# Create an importer
importer = ScriptImporter(registry)

# Add scripts
importer.add_script('library', library_source)
importer.add_script('indicator', indicator_source)
importer.add_script('main', strategy_source, is_main=True)

# Register the import_script function
registry.register('import_script', importer.import_script)

# Build and run the main script
context = importer.build_main_script()
context.compile()
context.run_setup()

# Process data
for i in range(len(data)):
    current_bar = data.iloc[i]
    historical_bars = data.iloc[:i+1]
    
    # Update data namespace
    context.namespaces.get('data').set_current_bar(current_bar)
    context.namespaces.get('data').set_all_bar(historical_bars)
    
    # Run process
    context.run_process()

# Get results
export = context.get_export()
outputs = context.generate_outputs()
metadata = context.generate_metadatas()
```

## Integration with Engine

The `ScriptImporter` is used by the `Engine` class to manage script imports:

```python
from script_engine import Engine

# Create an engine with imports
engine = Engine(
    data,
    main_script_str=strategy_source,
    imported_script={
        'library': library_source,
        'indicator': indicator_source
    }
)

# Run the strategy
results = engine.run()
```

## Script Import Syntax

In scripts, imports are done using the `import_script` function:

```python
def setup():
    global my_library
    my_library = import_script('library')

def process():
    # Use the imported library
    result = my_library.calculate_something(data.all.close)
```
