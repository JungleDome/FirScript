# Working with Namespaces

Namespaces are a core concept in FirScript that provide functionality to your scripts. They allow you to access data, perform calculations, visualize results, and execute trading actions.

## Understanding Namespaces

In FirScript, namespaces are objects that provide a collection of related functions and properties. They are accessed using dot notation, such as `data.close` or `ta.sma()`.

Namespaces serve several important purposes:

1. **Organization**: They group related functionality together
2. **Isolation**: They prevent naming conflicts with your script variables
3. **State Management**: They can maintain state between function calls
4. **Output Generation**: They can generate output after script execution

## Default Namespaces

FirScript provides several built-in namespaces:

### data

The `data` namespace provides access to price and volume data:

```python
# Access current bar data
current_close = data.close
current_high = data.high

# Access previous bar data
previous_close = data.close[1]
previous_high = data.high[1]

# Access all historical data
all_closes = data.all.close
```

### ta

The `ta` namespace provides technical analysis functions:

```python
# Calculate indicators
sma_value = ta.sma(data.all.close, length=20)
rsi_value = ta.rsi(data.all.close, length=14)
upper, middle, lower = ta.bollinger_bands(data.all.close, length=20, multiplier=2)
```

### input

The `input` namespace handles script input parameters:

```python
def setup():
    global length, threshold
    length = input.int("Length", 14)
    threshold = input.float("Threshold", 70.0)
```

### chart

The `chart` namespace provides visualization capabilities:

```python
# Plot indicators
chart.plot(sma_value, title="SMA", color=color.blue)
chart.line(support_level, color=color.green, style="dashed")
```

### color

The `color` namespace provides color constants:

```python
chart.plot(sma_value, color=color.blue)
chart.plot(rsi_value, color=color.red)
```

### strategy

The `strategy` namespace handles trading actions:

```python
if buy_condition:
    strategy.long()
elif sell_condition:
    strategy.short()
elif exit_condition:
    strategy.close()
```

### log

The `log` namespace provides logging capabilities:

```python
log.info("Processing bar")
log.debug(f"RSI value: {rsi_value}")
log.warning("Unusual market condition detected")
```

## Creating Custom Namespaces

FirScript allows you to extend its functionality by creating custom namespaces. This is a powerful feature that lets you add specialized functions and capabilities to your scripts.

### What are Custom Namespaces?

Custom namespaces are user-defined modules that provide additional functionality to scripts. They follow the same pattern as the built-in namespaces (`ta`, `data`, `chart`, etc.) but can implement any functionality you need.

Custom namespaces can:
- Provide additional technical indicators
- Implement custom trading signals
- Add specialized data processing functions
- Integrate with external systems
- Store and track custom state during script execution

### Creating a Basic Custom Namespace

To create a custom namespace, you need to inherit from the `BaseNamespace` class and implement your desired functionality:

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

#### Key Components

1. **Inherit from BaseNamespace**: All custom namespaces must inherit from `BaseNamespace`
2. **Initialize with shared dictionary**: The `shared` dictionary allows namespaces to share data
3. **Implement methods**: Add methods that provide the functionality you need
4. **Override generate_output (optional)**: Provide output data after script execution
5. **Override generate_metadata (optional)**: Provide metadata after script execution

### Registering Custom Namespaces with the Engine

Once you've created a custom namespace, you need to register it with the `Engine`:

```python
from firscript import Engine
import pandas as pd

# Create data
data = pd.DataFrame(...)

# Create engine
engine = Engine(data, main_script_str=script_source)

# Register custom namespace
engine.registry.register("signals", SignalsNamespace(engine.registry.shared))

# Run the script
results = engine.run()
```

### Using Custom Namespaces in Scripts

Once registered, you can use your custom namespace in scripts just like any built-in namespace:

```python
def setup():
    global fast_length, slow_length
    fast_length = input.int("Fast Length", 12)
    slow_length = input.int("Slow Length", 26)

def process():
    global fast_length, slow_length

    fast_ma = ta.ema(data.all.close, fast_length)
    slow_ma = ta.ema(data.all.close, slow_length)

    if signals.crossover(fast_ma, slow_ma):
        strategy.long()
    elif signals.crossunder(fast_ma, slow_ma):
        strategy.short()
```

### Accessing Shared Data

Custom namespaces can access shared data through the `shared` dictionary:

```python
class DataAnalysisNamespace(BaseNamespace):
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)

    def current_bar(self):
        """Get the current bar data"""
        return self.shared.get('data', {}).get('current')

    def historical_data(self):
        """Get all historical data"""
        return self.shared.get('data', {}).get('all')
```

## Namespace Output and Metadata

Namespaces can generate two types of information after script execution:

1. **Output**: Data generated during script execution, such as trading signals, chart plots, or log messages
2. **Metadata**: Information about the namespace itself, such as input parameters or configuration

### Accessing Namespace Output

When you run a script with the `Engine.run()` method, it returns a tuple containing the output and metadata:

```python
output, metadata = engine.run()

# Access namespace output
strategy_output = output.get("strategy", {})
chart_output = output.get("chart", [])
custom_output = output.get("custom", {})

# Access namespace metadata
input_metadata = metadata.get("input", {})
```

## Best Practices

When working with namespaces, follow these best practices:

1. **Use appropriate namespaces**: Use the right namespace for each task (e.g., `ta` for technical analysis, `chart` for visualization)
2. **Keep scripts organized**: Group related functionality by namespace
3. **Understand namespace scope**: Namespaces are available throughout the script execution
4. **Keep namespaces focused**: Each namespace should have a clear, single responsibility
5. **Use the shared dictionary**: Use the `shared` dictionary to share data between namespaces
6. **Implement output generation**: Override the `generate_output()` method to provide useful output
7. **Document your namespaces**: Provide clear documentation for your custom namespaces
8. **Follow naming conventions**: Use clear, descriptive names for your namespace methods
9. **Handle errors gracefully**: Catch and handle exceptions to prevent script failures
10. **Validate inputs**: Check input parameters to prevent unexpected behavior

### Example: Custom Technical Indicators Namespace

Here's a more complex example of a custom namespace that provides additional technical indicators:

```python
from firscript.namespaces.base import BaseNamespace
import pandas as pd
import numpy as np
from typing import Any, List, Tuple, override

class CustomIndicatorsNamespace(BaseNamespace):
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        self.calculations = []

    def keltner_channel(self,
                        price: pd.Series,
                        length: int = 20,
                        atr_length: int = 10,
                        multiplier: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Calculate Keltner Channels"""
        # Record the calculation
        self.calculations.append({
            "type": "keltner_channel",
            "params": {
                "length": length,
                "atr_length": atr_length,
                "multiplier": multiplier
            }
        })

        # Calculate EMA
        ema = pd.Series(price).rolling(window=length).mean().values

        # Calculate ATR
        high = self.shared.get('data', {}).get('all', {}).get('high', pd.Series())
        low = self.shared.get('data', {}).get('all', {}).get('low', pd.Series())
        close = price

        tr = pd.DataFrame()
        tr['h-l'] = high - low
        tr['h-pc'] = abs(high - close.shift(1))
        tr['l-pc'] = abs(low - close.shift(1))
        tr['tr'] = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        atr = tr['tr'].rolling(window=atr_length).mean()

        # Calculate bands
        upper = ema + multiplier * atr
        lower = ema - multiplier * atr

        return upper.tolist(), ema.tolist(), lower.tolist()

    @override
    def generate_output(self):
        """Return information about calculations performed"""
        return {
            "calculations": self.calculations
        }
```

This custom namespace could then be used in scripts:

```python
def setup():
    global length, atr_length, multiplier
    length = input.int("Length", 20)
    atr_length = input.int("ATR Length", 10)
    multiplier = input.float("Multiplier", 2.0)

def process():
    global length, atr_length, multiplier

    # Calculate Keltner Channels
    upper, middle, lower = indicators.keltner_channel(
        data.all.close,
        length=length,
        atr_length=atr_length,
        multiplier=multiplier
    )

    # Plot the channels
    chart.plot(upper[-1], title="Upper KC", color=color.red)
    chart.plot(middle[-1], title="Middle KC", color=color.blue)
    chart.plot(lower[-1], title="Lower KC", color=color.green)

    # Trading logic
    if data.close < lower[-1]:
        strategy.long()
    elif data.close > upper[-1]:
        strategy.short()
```
