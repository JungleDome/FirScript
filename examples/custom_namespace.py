from enum import Enum
from typing import override
import pandas as pd
import random
from script_engine.execution_input import ExecutionInputBase
from script_engine.namespaces.base import BaseNamespace
from script_engine.runtime import RuntimeEnvironment
from script_engine.parser import ScriptParser


# Define our own custom namespace
class CustomNamespace(BaseNamespace):
    def __init__(self):
        self.counter = 0

    def add_counter(self):
        self.counter += 1

    @override
    def generate_output(self):
        return {
            "output_text": "This is a custom output string.",
            "counter": self.counter,
        }


def main():
    # Create test data
    periods = 5
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-01-01", periods=periods),
            "close": [100 + 0.5 * i + random.random() for i in range(periods)],
        }
    )

    # Initialize parser
    parser = ScriptParser()
    strategy_script = parser.parse(
        """
def setup():
    pass

def process():
    custom.add_counter()
""",
        "main_script",
    )

    # Initialize runtime
    runtime = RuntimeEnvironment(
        script_definitions={"main_script": strategy_script},
        column_mapping={"close": "close"},
    )
    runtime.register_namespace("custom", CustomNamespace())

    print("=== Script Output ===")
    for i in range(len(data)):
        bar = data.iloc[0 : i + 1]
        current = data.iloc[i:i+1]
        result = runtime.run(
            "main_script",
            execution_input=ExecutionInputBase(current=current, all=bar),
        )
        print(f"Bar {i+1}: {result}")


main()
