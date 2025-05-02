# Namespace Registry API

The `NamespaceRegistry` class is responsible for managing namespaces in FirScript. It provides a central registry for all namespaces that scripts can access during execution.

## Class: NamespaceRegistry

```python
class NamespaceRegistry:
    def __init__(self):
        ...
```

The `NamespaceRegistry` manages the registration and retrieval of namespaces that provide functionality to scripts.

### Methods

#### register(name, namespace)

```python
def register(self, name: str, namespace: BaseNamespace | Callable) -> None:
    ...
```

Registers a namespace with the given name.

**Parameters**:
- **name** (`str`): The name that scripts will use to access this namespace
- **namespace** (`BaseNamespace | Callable`): The namespace object or callable function to register

**Example**:
```python
# Register a custom namespace
registry.register("signals", SignalsNamespace())

# Register a function as a namespace
registry.register("utils", my_utility_function)
```

#### register_default_namespaces(inputs_override, column_mapping)

```python
def register_default_namespaces(self, inputs_override: Optional[Dict[str, Any]], 
                               column_mapping: Optional[Dict[str, str]] = None) -> None:
    ...
```

Initializes and registers the default namespaces provided by FirScript.

**Parameters**:
- **inputs_override** (`Dict[str, Any]`, optional): Dictionary of input values to override defaults
- **column_mapping** (`Dict[str, str]`, optional): Mapping of standard column names to actual data column names

**Default Namespaces**:
- `ta`: Technical analysis functions
- `input`: Input parameter handling
- `chart`: Chart visualization
- `color`: Color constants
- `strategy`: Trading strategy actions
- `data`: Data access
- `log`: Logging utilities

#### get(name)

```python
def get(self, name: str) -> BaseNamespace:
    ...
```

Retrieves a namespace by name.

**Parameters**:
- **name** (`str`): The name of the namespace to retrieve

**Returns**:
- The namespace object

#### build()

```python
def build(self) -> dict[str, BaseNamespace]:
    ...
```

Creates a copy of all registered namespaces.

**Returns**:
- A dictionary mapping namespace names to namespace objects

#### generate_outputs(namespaces)

```python
@staticmethod
def generate_outputs(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
    ...
```

Generates outputs from all namespaces that support output generation.

**Parameters**:
- **namespaces** (`dict[str, BaseNamespace]`): Dictionary of namespaces

**Returns**:
- A dictionary mapping namespace names to their generated outputs

#### generate_metadatas(namespaces)

```python
@staticmethod
def generate_metadatas(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
    ...
```

Generates metadata from all namespaces that support metadata generation.

**Parameters**:
- **namespaces** (`dict[str, BaseNamespace]`): Dictionary of namespaces

**Returns**:
- A dictionary mapping namespace names to their generated metadata

## Creating Custom Namespaces

To create a custom namespace, you need to inherit from `BaseNamespace` and implement the required methods.

### BaseNamespace

```python
class BaseNamespace(ABC):
    def __init__(self, shared: dict[str, Any]):
        self.shared = shared

    @classmethod
    def generate_output(self) -> Optional[Any]:
        pass

    @classmethod
    def generate_metadata(self) -> Optional[Any]:
        pass
```

The `BaseNamespace` class is the base class for all namespaces in FirScript.

**Attributes**:
- **shared** (`dict[str, Any]`): A shared dictionary that all namespaces can access

**Methods**:
- **generate_output()**: Generate output data after script execution
- **generate_metadata()**: Generate metadata after script execution

### Example: Custom Namespace

```python
from firscript.namespaces.base import BaseNamespace
from typing import Any, override

class SignalsNamespace(BaseNamespace):
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        self.signals = []
    
    def crossover(self, fast, slow):
        """Detect when fast line crosses above slow line"""
        result = (fast > slow) & (fast.shift() <= slow.shift())
        if result:
            self.signals.append({"type": "crossover", "value": True})
        return result
    
    def crossunder(self, fast, slow):
        """Detect when fast line crosses below slow line"""
        result = (fast < slow) & (fast.shift() >= slow.shift())
        if result:
            self.signals.append({"type": "crossunder", "value": True})
        return result
    
    @override
    def generate_output(self):
        """Return all signals generated during execution"""
        return {"signals": self.signals}
```

### Registering Custom Namespaces

```python
from firscript import Engine, NamespaceRegistry
import pandas as pd

# Create data
data = pd.DataFrame(...)

# Create engine with custom namespace registry
engine = Engine(
    data,
    main_script_str=script_source
)
engine.registry.register("signals", SignalsNamespace(engine.registry.shared))

# Run the script
results = engine.run()
```

## Default Namespaces

FirScript provides several built-in namespaces:

### ta

Technical analysis functions for calculating indicators.

```python
# In script
sma_value = ta.sma(data.all.close, length=20)
rsi_value = ta.rsi(data.all.close, length=14)
```

### input

Handles script input parameters and configuration.

```python
# In script setup()
length = input.int("Length", 14)
threshold = input.float("Threshold", 70.0)
name = input.text("Name", "My Strategy")
enabled = input.bool("Enabled", True)
```

### chart

Provides chart visualization capabilities.

```python
# In script
chart.plot(sma_value, title="SMA", color=color.blue)
chart.line(support_level, color=color.green, style="dashed")
```

### color

Provides color constants for chart visualization.

```python
# In script
chart.plot(sma_value, color=color.blue)
chart.plot(rsi_value, color=color.red)
```

### strategy

Handles trading actions and position management.

```python
# In script
if buy_condition:
    strategy.long()
elif sell_condition:
    strategy.short()
elif exit_condition:
    strategy.close()
```

### data

Provides access to price and volume data.

```python
# In script
current_close = data.close
previous_close = data.close[1]
all_closes = data.all.close
```

### log

Provides logging capabilities.

```python
# In script
log.info("Processing bar")
log.debug(f"RSI value: {rsi_value}")
log.warning("Unusual market condition detected")
```
