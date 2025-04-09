"""
MA Crossover Strategy
Demonstrates state persistence and basic moving average crossover logic
"""

# Import an indicator
#const sma = import 'sma_indicator'


def setup():
    """Initialize strategy state"""
    global trade_count, last_position, fast_length, slow_length
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)
    trade_count = 0
    last_position = None
    print(f"Strategy initialized with fast={fast_length}, slow={slow_length}")

def process():
    """Process each bar"""
    global trade_count, last_position
    
    # Get indicator values
    fast_ma = ta.sma(data.all.close, fast_length).iloc[-1]
    slow_ma = ta.sma(data.all.close, slow_length).iloc[-1]
    close = data.current.close
    
    # Plot the moving averages
    chart.plot(fast_ma, color=color.blue, title="Fast MA")
    chart.plot(slow_ma, color=color.red, title="Slow MA")
    
    # Trading logic - MA crossover
    if fast_ma > slow_ma and last_position != 'long':
        strategy.long()
        last_position = 'long'
        trade_count += 1
    elif fast_ma < slow_ma and last_position != 'short':
        strategy.short()
        last_position = 'short'
        trade_count += 1
        
    # Debug output
    print(f"{data.current.timestamp}: Close={close:.2f} | Fast MA={fast_ma:.2f} | Slow MA={slow_ma:.2f} | Trades={trade_count}")