"""
Example demonstrating how to run a strategy script that imports another script
"""
import random
import sys
import os
import pandas as pd

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from script_engine.engine import ScriptEngine

def main():
    # Create sample price data
    periods = 50
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })

    # Read the strategy script
    with open('examples/simple_strategy_with_import.py', 'r') as f:
        strategy_script = f.read()
    
    # Read the library script that will be imported
    with open('examples/simple_library.py', 'r') as f:
        library_script = f.read()

    # Initialize engine with both scripts
    # The key in the dictionary is the script ID that will be used in import_script()
    engine = ScriptEngine({
        'main': strategy_script,
        'simple_library': library_script
    }, 'main')
    
    # Run the strategy
    result = engine.run(data)
    print("\nStrategy execution completed:")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
