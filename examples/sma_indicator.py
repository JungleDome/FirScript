# Simple Moving Average Indicator
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

# Calculate SMA on close prices
export = calculate_sma(bar.close, 14) 