# Quick Start Guide

This guide will help you get started with FirScript by walking through a simple example.

## Basic Usage

Here's a simple example of how to use the FirScript:

```python
from firscript import Engine
import pandas as pd
import numpy as np

# Create some sample data
dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
data = pd.DataFrame({
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 102,
    'low': np.random.randn(100).cumsum() + 98,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100)
}, index=dates)

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
results = engine.run()

# Print the results
print(results)
```

## Understanding the Components

### 1. Engine

The `Engine` class is the main entry point for the FirScript. It takes care of:

- Parsing the script
- Setting up the execution environment
- Running the script for each bar in the data
- Collecting and returning the results

### 2. Script Structure

Scripts in FirScript follow a specific structure:

- `setup()` function: Called once at the beginning to initialize parameters
- `process()` function: Called for each bar in the data

### 3. Namespaces

The engine provides several namespaces that scripts can use:

- `input`: For defining input parameters
- `data`: For accessing price and volume data
- `ta`: For technical analysis functions
- `strategy`: For executing trading actions
- `chart`: For visualization

### 4. Results

The `run()` method returns a dictionary containing the results of the strategy execution, including:

- Trades
- Positions
- Performance metrics
- Chart data

## Next Steps

Now that you've seen a basic example, you can:

1. Check out the [Examples](examples.md) section for more complex use cases
2. Learn about the [Scripting Conventions](../user_guide/scripting_conventions.md)
3. Explore the [API Reference](../api/engine.md) for detailed documentation
