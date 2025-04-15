"""
Strategy With Indicator Import Example
Demonstrates how to import and use an indicator in a strategy
"""

def setup():
    """Initialize strategy parameters"""
    global rsi_length, threshold, sma_indicator
    
    # Import the SMA indicator
    sma_indicator = import_script('simple_indicator')
    
    # Define strategy parameters
    rsi_length = input.int('RSI Length', 14)
    threshold = input.int('Threshold', 2)
    
    print(f"Strategy initialized with RSI length={rsi_length}, threshold={threshold}")

def process():
    """Process each bar"""
    # Calculate RSI using the current data
    rsi_value = ta.rsi(data.all.close, rsi_length)[-1]
    
    # Get the current SMA value from the imported indicator
    # The indicator's process() function returns the SMA value
    sma_value = sma_indicator
    
    # Plot indicators
    chart.plot(rsi_value, color=color.orange, title="RSI")
    
    # Trading logic using both our RSI and the imported SMA indicator
    if rsi_value < 30 and data.current.close > sma_value + threshold:
        strategy.long()
    elif rsi_value > 70 and data.current.close < sma_value - threshold:
        strategy.short()
        
    # Debug output
    print(f"{data.current.timestamp}: Close={data.current.close:.2f} | RSI={rsi_value:.2f} | SMA={sma_value:.2f}")
