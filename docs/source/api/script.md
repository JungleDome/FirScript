# Script API

The `Script` class and related types represent parsed scripts in the FirScript.

## Enum: ScriptType

```python
class ScriptType(Enum):
    STRATEGY = "strategy"
    INDICATOR = "indicator"
    LIBRARY = "library"
```

Represents the type of a script:

- **STRATEGY**: A script that defines trading logic with `setup()` and `process()` functions and can use the strategy namespace.
- **INDICATOR**: A script that calculates technical indicators with `setup()` and `process()` functions but cannot use the strategy namespace.
- **LIBRARY**: A script that exports functions or other objects for use by other scripts.

## Class: ScriptMetadata

```python
@dataclass
class ScriptMetadata:
    """Stores metadata parsed from the script source."""
    id: str  # Usually the name/path provided during import/load
    name: str # Optional descriptive name from script
    type: ScriptType
    exports: Set[str] = field(default_factory=set) # Variables intended for export
    imports: Dict[str, str] = field(default_factory=dict) # Alias -> script_id mapping
```

Stores metadata extracted from a script during parsing.

### Attributes

- **id** (`str`): The identifier for the script, usually the name or path provided during import/load.
- **name** (`str`): An optional descriptive name for the script.
- **type** (`ScriptType`): The type of the script (STRATEGY, INDICATOR, or LIBRARY).
- **exports** (`Set[str]`): A set of variable names that are exported by the script.
- **imports** (`Dict[str, str]`): A dictionary mapping import aliases to script IDs.

## Class: Script

```python
@dataclass
class Script:
    """Represents a parsed script with its source code and metadata."""
    source: str
    metadata: ScriptMetadata
```

Represents a parsed script with its source code and metadata.

### Attributes

- **source** (`str`): The source code of the script.
- **metadata** (`ScriptMetadata`): The metadata extracted from the script during parsing.

### Example Usage

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

## Working with Scripts

Scripts are typically created by the `ScriptParser` and then passed to the `Engine` or `ScriptImporter` for execution. You can also create `Script` objects directly if you have pre-parsed scripts.

### Creating Scripts Manually

```python
from firscript import Script, ScriptMetadata, ScriptType

# Create script metadata
metadata = ScriptMetadata(
    id="my_script",
    name="My Custom Script",
    type=ScriptType.INDICATOR,
    exports=set(),
    imports={}
)

# Create a script
script = Script(
    source="def setup():\n    global length\n    length = 14\n\ndef process():\n    pass",
    metadata=metadata
)
```

### Using Scripts with the Engine

```python
from firscript import Engine, Script

# Create an engine with pre-parsed scripts
engine = Engine(data, scripts=[script1, script2])

# Run the scripts
results = engine.run()
```
