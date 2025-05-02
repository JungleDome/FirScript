# Examples

This section provides examples of how to use the FirScript for various use cases.

## Simple Strategy

```python
from firscript import Engine
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv', index_col='date', parse_dates=True)

# Define a simple moving average crossover strategy
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

# Create an engine instance
engine = Engine(data, main_script_str=strategy_source)

# Run the strategy
results = engine.run()

# Print the results
print(results)
```

## Simple Indicator

```python
from firscript import Engine
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv', index_col='date', parse_dates=True)

# Define a simple RSI indicator
indicator_source = """
def setup():
    global length, overbought, oversold
    length = input.int('RSI Length', 14)
    overbought = input.float('Overbought Level', 70)
    oversold = input.float('Oversold Level', 30)

def process():
    global length, overbought, oversold

    # Calculate RSI
    rsi_value = ta.rsi(data.all.close, length)[-1]

    # Plot the indicator
    chart.plot(rsi_value, title="RSI")
    chart.hline(overbought, color=color.red, title="Overbought")
    chart.hline(oversold, color=color.green, title="Oversold")
"""

# Create an engine instance
engine = Engine(data, main_script_str=indicator_source)

# Run the indicator
results = engine.run()

# Access the chart data
chart_data = results.get('chart', {})
print(chart_data)
```

## Using a Library

```python
from firscript import Engine
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv', index_col='date', parse_dates=True)

# Define a library for custom functions
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

# Define a strategy that uses the library
strategy_source = """
def setup():
    global period
    period = input.int('Period', 14)
    myLibrary = import_script('lib')

def process():
    global period

    # Use the imported library functions
    momentum = myLibrary.momentum(data.all.close, period)
    roc = myLibrary.roc(data.all.close, period)

    # Trading logic
    if momentum > 0 and roc > 0:
        strategy.long()
    elif momentum < 0 and roc < 0:
        strategy.short()

    # Plot the indicators
    chart.plot(momentum, title="Momentum")
    chart.plot(roc, title="Rate of Change")
"""

# Create an engine instance with the library
engine = Engine(
    data,
    main_script_str=strategy_source,
    import_scripts={
        'lib': library_source
    }
)

# Run the strategy
results = engine.run()

# Print the results
print(results)
```

## Custom Namespace

FirScript allows you to extend its functionality with custom namespaces. Here's a simple example:

```python
from firscript import Engine
import pandas as pd

# Define a custom namespace
class CustomNamespace:
    def __init__(self):
        self.name = "custom"

    def calculate_custom_indicator(self, values, param1=10, param2=20):
        """A custom indicator calculation"""
        if len(values) < max(param1, param2):
            return 0
        # Custom calculation logic
        result = sum(values[-param1:]) / param1 - sum(values[-param2:]) / param2
        return result

# Create an engine with a strategy that uses the custom namespace
engine = Engine(data, main_script_str=strategy_source)

# Register the custom namespace
engine.registry.register("custom", CustomNamespace())

# Run the strategy
results = engine.run()
```

For more detailed information on creating and using custom namespaces, see the [Namespaces](../user_guide/namespaces.md#creating-custom-namespaces) guide.

## More Examples

For more examples, check out the [examples directory](https://github.com/JungleDome/FirScript/tree/main/examples) in the GitHub repository.
