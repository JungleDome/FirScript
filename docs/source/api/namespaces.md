# Namespaces API

FirScript provides several built-in namespaces that scripts can use to access data, perform calculations, and execute trading actions. This page documents the available namespaces and their functionality.

## BaseNamespace

All namespaces in FirScript inherit from the `BaseNamespace` class, which provides the basic structure and shared functionality.

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

## Data Namespace

The `data` namespace provides access to price and volume data.

### Properties

- **current**: The current bar data as a pandas Series
- **all**: All historical bars up to the current bar as a pandas DataFrame
- **open**: Historical open prices with index 0 being the most recent
- **high**: Historical high prices with index 0 being the most recent
- **low**: Historical low prices with index 0 being the most recent
- **close**: Historical close prices with index 0 being the most recent
- **volume**: Historical volume with index 0 being the most recent
- **timestamp**: Historical timestamps with index 0 being the most recent

### Usage

```python
# Access current bar data
current_close = data.close
current_open = data.open

# Access previous bar data
previous_close = data.close[1]
previous_open = data.open[1]

# Access all historical data
all_closes = data.all.close
```

## Technical Analysis Namespace

The `ta` namespace provides technical analysis functions for calculating indicators.

### Methods

#### sma(series, length)

Simple Moving Average.

```python
sma_value = ta.sma(data.all.close, length=20)
```

#### ema(series, length)

Exponential Moving Average.

```python
ema_value = ta.ema(data.all.close, length=20)
```

#### rsi(series, length)

Relative Strength Index.

```python
rsi_value = ta.rsi(data.all.close, length=14)
```

#### atr(dataframe, length)

Average True Range.

```python
atr_value = ta.atr(data.all, length=14)
```

#### macd(series, fast_length, slow_length, signal_length)

Moving Average Convergence Divergence.

```python
macd_line, signal_line, histogram = ta.macd(data.all.close, fast_length=12, slow_length=26, signal_length=9)
```

#### bollinger_bands(series, length, multiplier)

Bollinger Bands.

```python
upper, middle, lower = ta.bollinger_bands(data.all.close, length=20, multiplier=2)
```

## Input Namespace

The `input` namespace handles script input parameters and configuration.

### Methods

#### int(name, default, **kwargs)

Define an integer input parameter.

```python
length = input.int("Length", 14)
```

#### float(name, default, **kwargs)

Define a float input parameter.

```python
threshold = input.float("Threshold", 70.0)
```

#### text(name, default, **kwargs)

Define a text input parameter.

```python
name = input.text("Name", "My Strategy")
```

#### bool(name, default, **kwargs)

Define a boolean input parameter.

```python
enabled = input.bool("Enabled", True)
```

## Chart Namespace

The `chart` namespace provides chart visualization capabilities.

### Methods

#### plot(series, title, color, linewidth)

Plot a series on the chart.

```python
chart.plot(sma_value, title="SMA", color=color.blue, linewidth=1)
```

#### line(price, **kwargs)

Draw a horizontal line on the chart.

```python
chart.line(support_level, color=color.green, style="dashed")
```

#### hline(price, **kwargs)

Draw a horizontal line on the chart (alias for line).

```python
chart.hline(resistance_level, color=color.red, style="dashed")
```

#### get_plots()

Get all registered plots for rendering.

```python
plots = chart.get_plots()
```

## Color Namespace

The `color` namespace provides color constants for chart visualization.

### Constants

- **red**: Red color
- **green**: Green color
- **blue**: Blue color
- **yellow**: Yellow color
- **purple**: Purple color
- **orange**: Orange color
- **black**: Black color
- **white**: White color
- **gray**: Gray color

### Usage

```python
chart.plot(sma_value, color=color.blue)
chart.plot(rsi_value, color=color.red)
```

## Strategy Namespace

The `strategy` namespace handles trading actions and position management.

### Methods

#### long(**kwargs)

Enter a long position.

```python
strategy.long(size=1.0)
```

#### short(**kwargs)

Enter a short position.

```python
strategy.short(size=1.0)
```

#### close(**kwargs)

Close current position.

```python
strategy.close()
```

#### position()

Get current position info.

```python
current_position = strategy.position()
position_size = current_position['size']
```

### Output

The strategy namespace generates output containing:

- **position**: Current position information
- **orders**: List of all orders executed during the script run

## Log Namespace

The `log` namespace provides logging capabilities.

### Methods

#### info(message)

Log an informational message.

```python
log.info("Processing bar")
```

#### warning(message)

Log a warning message.

```python
log.warning("Unusual market condition detected")
```

#### error(message)

Log an error message.

```python
log.error("Failed to calculate indicator")
```

### Output

The log namespace generates output containing:

- **info**: List of info messages
- **warning**: List of warning messages
- **error**: List of error messages

## Creating Custom Namespaces

You can create custom namespaces to extend FirScript's functionality. Here's an example of a custom namespace:

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

To implement and apply a custom namespace in the script.

Method 1 (__Recommended__): Register it with the `Engine`:

```python
from firscript import Engine

# Create engine with custom namespace
engine = Engine(
    data,
    main_script_str=script_source
)

# Register custom namespace
engine.registry.register("signals", SignalsNamespace(engine.registry.shared))

# Run the script
results = engine.run()
```

Method 2: Register it with the `NamespaceRegistry`:

```python
from firscript import Engine, NamespaceRegistry

# Create a namespace registry
registry = NamespaceRegistry()

# Register default namespaces
registry.register_default_namespaces({})

# Register custom namespace
registry.register("signals", SignalsNamespace(registry.shared))

# Create engine with custom namespace registry
engine = Engine(
    data,
    main_script_str=script_source
)

# Set the custom namespace registry
engine.registry = registry

# Run the script
results = engine.run()
```

Then, in your script, you can use the custom namespace:

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
