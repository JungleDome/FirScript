# TradePilot Script Engine

A Python-based backtesting engine with a custom scripting system inspired by TradingView's Pine Script v5.

## Features

- Support for both strategy and indicator scripts
- Built-in technical analysis functions
- Configurable inputs
- Chart plotting capabilities
- Strategy execution with order management
- Indicator script importing

## Project Structure

```
script_engine/
├── script.py      # Base script classes and interfaces
├── parser.py      # Script parsing and validation
└── runtime.py     # Script execution environment

examples/
├── simple_strategy.py  # Example strategy script
└── sma_indicator.py    # Example indicator script
```

## Script Types

### Strategy Scripts
- Must contain `setup()` and `process(bar)` functions
- Can use all available namespaces
- Cannot use `input` functions inside `process()`
- Must use at least one `strategy` function

### Indicator Scripts
- Must export exactly one value (named `export`)
- Cannot use `strategy` functions
- Can use `chart.plot()` for visualization
- Can be imported by strategy scripts

## Available Namespaces

- `ta`: Technical analysis functions (e.g., `ta.ema()`, `ta.rsi()`)
- `input`: Configurable inputs (`input.int()`, `input.float()`, etc.)
- `chart`: Drawing/plotting functions (`chart.plot()`)
- `color`: Color constants (`color.red`, `color.blue`, etc.)
- `strategy`: Order management (`strategy.long()`, `strategy.short()`, etc.)

## Usage

```python
from script_engine.parser import ScriptParser
from script_engine.runtime import RuntimeEnvironment

# Create parser and runtime
parser = ScriptParser()
runtime = RuntimeEnvironment()

# Parse and execute a script
with open("examples/simple_strategy.py") as f:
    source = f.read()
    script = parser.parse(source)
    result = runtime.execute_script(script)
```

## Example Scripts

### Simple Strategy
```python
def setup():
    fast_length = input.int("Fast MA Length", 10)
    slow_length = input.int("Slow MA Length", 20)
    return {"fast_length": fast_length, "slow_length": slow_length}

def process(bar):
    fast_ma = ta.sma(bar.close, setup.fast_length)
    slow_ma = ta.sma(bar.close, setup.slow_length)
    
    if fast_ma > slow_ma:
        strategy.long()
    elif fast_ma < slow_ma:
        strategy.short()
```

### SMA Indicator
```python
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)
```

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest`

## License

MIT License 