from enum import Enum
import pandas as pd
import random
from script_engine.runtime import RuntimeEnvironment, RuntimeExecutionInput
from script_engine.parser import ScriptParser
from script_engine.script import ScriptType

# Mock namespaces for testing
class InputNamespace:
    @staticmethod
    def int(name, default):
        return default

class TANamespace:
    @staticmethod
    def sma(series, length):
        return series.rolling(length).mean()
    
    @staticmethod 
    def rsi(series, length):
        diff = series.diff()
        up = diff.clip(lower=0)
        down = -diff.clip(upper=0)
        rs = up.rolling(length).mean() / down.rolling(length).mean()
        return 100 - (100 / (1 + rs))

class StrategyNamespace:
    def __init__(self):
        self.position_size = 0
    
    def long(self):
        self.position_size = 1
        print("Entered long position")
        
    def short(self):
        self.position_size = -1
        print("Entered short position")
        
class ChartNamespace:
    @staticmethod
    def plot(series, color, title):
        print("Plot chart")
        
class ColorNamespace:
    red = '#ff0000',
    blue = '#0000ff',
    green = '#00ff00'

def main():
    # Create realistic test data with enough bars
    periods = 50  # Enough for all calculations
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })

    # Initialize runtime
    runtime = RuntimeEnvironment(column_mapping={'close': 'close'})
    runtime.register_namespace('ta', TANamespace())
    runtime.register_namespace('strategy', StrategyNamespace())
    runtime.register_namespace('input', InputNamespace())
    runtime.register_namespace('chart', ChartNamespace())
    runtime.register_namespace('color', ColorNamespace())

    # Parse and test strategy script
    with open('examples/simple_strategy.py') as f:
        strategy_source = f.read()
        
    parser = ScriptParser()
    strategy_script = parser.parse(strategy_source)

    print("=== Testing Strategy Script ===")
    for i in range(len(data)):
        bar = data.iloc[0:i+1]
        runtime.execute_script(
            strategy_script,
            execution_input=RuntimeExecutionInput(
                current_bar=data.iloc[i],
                all_bar=bar
            )
        )

    # Parse and test indicator script    
    with open('examples/simple_indicator.py') as f:
        indicator_source = f.read()
        
    indicator_script = parser.parse(indicator_source)

    print("\n=== Testing Indicator Script ===")
    for i in range(5, len(data)):  # Start from 5 to have enough data for calculations
        bar = data.iloc[0:i+1]
        result = runtime.execute_script(
            indicator_script,
            execution_input=RuntimeExecutionInput(
                current_bar=data.iloc[i],
                all_bar=bar
            )
        )
        # print(f"Bar {i}: {result}")

main()