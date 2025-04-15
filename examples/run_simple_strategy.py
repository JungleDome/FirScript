"""
Simple example demonstrating how to run a strategy script
"""
import random
import pandas as pd
from script_engine.engine import ScriptEngine

def main():
    # Create sample price data
    periods = 50
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })

    # Read the strategy script
    with open('examples/simple_strategy.py', 'r') as f:
        strategy_script = f.read()

    # Initialize engine
    engine = ScriptEngine({'main': strategy_script}, 'main')
    
    # Run the strategy
    result = engine.run(data)
    print("\nStrategy execution completed:")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()