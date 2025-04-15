# Scripting Conventions

This document outlines the conventions for writing scripts for the TradePilot ScriptEngine.

## General Rules

1. **Script Types**:
   - **Strategy**: Must define `setup()` and `process()` functions and can use the strategy namespace
   - **Indicator**: Must define `setup()` and `process()` functions but cannot use the strategy namespace
   - **Library**: Must assign to an `export` variable and cannot have setup/process functions
   - Mixing different script type features is not allowed

2. **Reserved Variable Names**:
   - Variables with names in the format `__variable_name__` (double underscores at both start and end) are reserved for system use
   - Scripts cannot export variables with this naming pattern
   - This applies to both direct exports (`export = __some_var__`) and dictionary keys in exports (`export = {"__key__": value}`)

3. **State Management**:
   - Variables declared at the top level persist between executions
   - Use the `global` keyword to modify state variables within functions
   - Avoid naming conflicts with runtime-provided namespaces

   ### State Initialization Best Practice

   - **All variable declarations must be inside the `setup()` or `process()` functions.**
   - Use the `global` keyword inside both `setup()` and `process()` to access or modify persistent state variables.
   - Do **not** declare any variables at the top level of the script (outside functions).
   - The parser will issue warnings if any variables are declared outside functions.

   **Example:**
   ```python
   def setup():
       global fast_length, slow_length, trade_count, last_position
       fast_length = input.int('Fast MA Length', 10)
       slow_length = input.int('Slow MA Length', 20)
       trade_count = 0
       last_position = None

   def process():
       global fast_length, slow_length, trade_count, last_position
       # Your trading logic here
   ```

3. **Inputs**:
   - Declare inputs using `input.<type>(name, default)` inside the `setup()` function
   - Inputs are read-only after declaration
   - Access inputs directly by their declared name

## Strategy Scripts

### Required Structure
```python
def setup():
    """Called once before first process()"""
    global param1, param2, my_state
    param1 = input.int('param1', 14)
    param2 = input.float('param2', 0.5)
    my_state = initialize_value()

def process():
    """Called for each bar"""
    global param1, param2, my_state
    # Trading logic here
    if condition:
        strategy.long()
```

### Rules:
- Must contain `setup()` and `process()` functions
- `process()` receives bar data as a pandas Series, it can be accessed through data.current, data.all
- Use strategy.* namespace for trading actions
- Input functions cannot be used in `process()`

## Indicator Scripts

### Required Structure
```python
def setup():
    """Initialize indicator parameters"""
    global length
    length = input.int('Length', 14)

def process():
    """Process each bar"""
    # Calculate indicator value
    sma_value = ta.sma(data.all.close, length)[-1]

    # Plot the indicator
    chart.plot(sma_value, color=color.blue, title="SMA")
```

### Rules:
- Must contain `setup()` and `process()` functions (same as strategy)
- Cannot use strategy.* namespace
- Can use chart.* namespace for visualization
- Can be imported by other scripts

## Library Scripts

### Required Structure
```python
def calculate_average(values):
    """Calculate the average of a list of values"""
    if not values:
        return 0
    return sum(values) / len(values)

def calculate_momentum(values, period=14):
    """Calculate momentum: current value - value 'period' bars ago"""
    if len(values) < period:
        return 0
    return values[-1] - values[-period]

# Export the functions as a dictionary
export = {
    "average": calculate_average,
    "momentum": calculate_momentum
}
```

### Rules:
- Must assign to exactly one `export` variable
- Cannot have setup() or process() functions
- Cannot use strategy.* namespace
- Export can be any Python object (function, dictionary, class, etc.)
- The value of the export variable is returned when the script is executed
- Primarily used for code reuse across scripts

## Namespace Design Principles

1. **Independence**
   - Namespaces are self-contained and stateless (except for their own internal state)
   - Namespaces cannot access script variables directly
   - All required data must be passed explicitly as parameters

2. **Available Namespaces**

- **ta**: Technical analysis functions
  - Example: `ta.sma(data.current.close, length=20)`
  - All indicators require explicit price/volume data

- **input**: Input configuration
  - Example: `input.int("period", 14)`
  - Returns configured values, does not store state

- **chart**: Visualization functions
  - Example: `chart.plot(my_sma, color=color.blue)`
  - All values must be passed explicitly

- **color**: Color constants
  - Pure constants, no state or script interaction

- **strategy**: Trading actions
  - Example: `strategy.long(data.current.close, size=1.0)`
  - Maintains only internal position/order state

## Best Practices

1. Keep scripts focused on a single purpose
2. Document input parameters
3. Initialize state in setup()
4. Use descriptive variable names
