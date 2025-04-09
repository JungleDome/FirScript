"""
Simple Moving Average Indicator
Calculates SMA of closing prices for given length
"""

# Input parameter
length = input.int('Length', 14)

# Calculate SMA using current bar's close price
sma_value = ta.sma(data.all.close, length)

# Export the indicator value
export = sma_value
