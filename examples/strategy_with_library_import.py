"""
Simple Strategy With Import Example
Demonstrates how to import and use another script (library) in a strategy
"""

def setup():
    """Initialize strategy parameters"""
    global fast_length, slow_length, momentum_threshold, utils
    
    # Import the utility library
    utils = import_script('simple_library')
    
    # Define strategy parameters
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)
    momentum_threshold = input.int('Momentum Threshold', 1)
    
    print(f"Strategy initialized with fast={fast_length}, slow={slow_length}, momentum_threshold={momentum_threshold}")

def process():
    """Process each bar"""
    # Get close prices
    close_prices = data.all.close.tolist()
    
    # Calculate indicators using standard TA functions
    fast_ma = ta.sma(data.all.close, fast_length)[-1]
    slow_ma = ta.sma(data.all.close, slow_length)[-1]
    
    # Use imported library functions for additional indicators
    # Access the functions using dictionary keys
    momentum = utils.momentum(close_prices, fast_length)
    roc = utils.roc(close_prices, slow_length)
    
    # Plot indicators
    chart.plot(fast_ma, color=color.blue, title="Fast MA")
    chart.plot(slow_ma, color=color.red, title="Slow MA")
    chart.plot(momentum, color=color.green, title="Momentum")
    chart.plot(roc, color=color.purple, title="ROC")
    
    # Trading logic combining standard indicators with library functions
    if fast_ma > slow_ma and momentum > momentum_threshold:
        strategy.long()
    elif fast_ma < slow_ma and momentum < -momentum_threshold:
        strategy.short()
        
    # Debug output
    print(f"{data.current.timestamp}: Close={data.current.close:.2f} | Fast MA={fast_ma:.2f} | Slow MA={slow_ma:.2f}")
    print(f"Momentum={momentum:.2f} | ROC={roc:.2f}%")
