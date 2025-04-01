# Simple moving average crossover strategy
def setup():
    # Define inputs
    fast_length = input.int("Fast MA Length", 10)
    slow_length = input.int("Slow MA Length", 20)
    
    # Import an indicator
    const sma = import 'sma_indicator'
    
    # Store inputs for later use
    return {
        "fast_length": fast_length,
        "slow_length": slow_length,
        "sma": sma
    }

def process(bar):
    # Get the SMAs
    fast_ma = ta.sma(bar.close, setup.fast_length)
    slow_ma = ta.sma(bar.close, setup.slow_length)
    
    # Plot the moving averages
    chart.plot(fast_ma, color=color.blue, title="Fast MA")
    chart.plot(slow_ma, color=color.red, title="Slow MA")
    
    # Trading logic
    if fast_ma > slow_ma:
        strategy.long()
    elif fast_ma < slow_ma:
        strategy.short() 