import pytest
import os 
print(os.getcwd())
from script_engine.parser import ScriptParser
from script_engine.runtime import RuntimeEnvironment
from script_engine.script import ScriptType

@pytest.fixture
def parser():
    return ScriptParser()

@pytest.fixture
def runtime():
    return RuntimeEnvironment()

@pytest.fixture
def valid_strategy_script():
    return """
def setup():
    length = input.int("Length", 14)
    return {"length": length}

def process(bar):
    if ta.sma(bar.close, setup.length) > bar.close:
        strategy.long()
"""

@pytest.fixture
def valid_indicator_script():
    return """
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)
"""

@pytest.fixture
def invalid_strategy_script():
    return """
def setup():
    return {}

def process(bar):
    length = input.int("Length", 14)  # Invalid: input in process()
    if ta.sma(bar.close, length) > bar.close:
        strategy.long()
"""

@pytest.fixture
def invalid_indicator_script():
    return """
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)
export2 = calculate_sma(bar.close, 20)  # Invalid: multiple exports
""" 