# Engine API

The `Engine` class is the main entry point for the FirScript. It handles the initialization of the script environment, parsing of scripts, and execution of the trading logic.

## Class: Engine

```python
class Engine:
    def __init__(self, data: pd.DataFrame, main_script_str: str = None, 
                 import_scripts: dict[str, str] = {}, scripts: list[Script] = None, 
                 inputs_override: dict[str, Any] = None, column_mapping: dict[str, str] = None):
        ...
```

### Parameters

- **data** (`pd.DataFrame`): The price and volume data to run the script on. Must be a non-empty pandas DataFrame.
- **main_script_str** (`str`, optional): The source code of the main script to run.
- **import_scripts** (`dict[str, str]`, optional): A dictionary mapping script names to their source code for scripts that will be imported by the main script.
- **scripts** (`list[Script]`, optional): A list of pre-parsed `Script` objects to use instead of parsing from source.
- **inputs_override** (`dict[str, Any]`, optional): A dictionary of input values to override the defaults specified in the script.
- **column_mapping** (`dict[str, str]`, optional): A dictionary mapping standard column names to the actual column names in the data DataFrame.

### Methods

#### run()

```python
def run(self):
    ...
```

Runs the script on the provided data.

**Returns**:
- If the script is a library script, returns the exported value.
- Otherwise, returns a tuple containing:
  - The result dictionary with outputs from all namespaces
  - A metadata dictionary with information about the script execution

### Example Usage

```python
import pandas as pd
from script_engine import Engine

# Create sample data
data = pd.DataFrame({
    'timestamp': pd.date_range('2023-01-01', periods=100),
    'open': [100 + i*0.1 for i in range(100)],
    'high': [100 + i*0.1 + 0.05 for i in range(100)],
    'low': [100 + i*0.1 - 0.05 for i in range(100)],
    'close': [100 + i*0.1 + 0.02 for i in range(100)],
    'volume': [1000 + i for i in range(100)]
})

# Define a simple strategy
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
results, metadata = engine.run()

# Print the results
print(results)
```

## Advanced Usage

### Custom Column Mapping

If your data DataFrame has column names that don't match the standard names (open, high, low, close, volume), you can provide a mapping:

```python
column_mapping = {
    'open': 'Open Price',
    'high': 'High Price',
    'low': 'Low Price',
    'close': 'Close Price',
    'volume': 'Volume'
}

engine = Engine(data, main_script_str=strategy_source, column_mapping=column_mapping)
```

### Input Overrides

You can override the default input values specified in the script:

```python
inputs_override = {
    'Fast MA Length': 5,
    'Slow MA Length': 15
}

engine = Engine(data, main_script_str=strategy_source, inputs_override=inputs_override)
```

### Importing Scripts

You can import other scripts to use in your main script:

```python
library_source = """
def calculate_momentum(values, period=14):
    if len(values) < period:
        return 0
    return values[-1] - values[-period]

export = {
    "momentum": calculate_momentum
}
"""

strategy_source = """
def setup():
    global period, myLibrary
    period = input.int('Period', 14)
    myLibrary = import_script('lib')

def process():
    global period
    momentum = myLibrary.momentum(data.all.close, period)
    
    if momentum > 0:
        strategy.long()
    elif momentum < 0:
        strategy.short()
"""

engine = Engine(
    data, 
    main_script_str=strategy_source,
    import_scripts={'lib': library_source}
)
```
