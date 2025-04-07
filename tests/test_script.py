import pytest
from script_engine.script import StrategyScript, IndicatorScript

@pytest.fixture
def strategy_script():
    # Mock setup and process functions
    def setup_fn():
        pass

    def process_fn(bar):
        return True

    return StrategyScript("source_code", setup_fn, process_fn)

def test_strategy_script_validate(strategy_script):
    assert strategy_script.validate()  # Should pass validation

def test_strategy_script_setup(strategy_script):
    # Mock setup function should be called without errors
    strategy_script.setup()

def test_strategy_script_process(strategy_script):
    # Test process method
    result = strategy_script.process("bar_data")
    assert result is None  # Should return None, even it is returned True on mock process_fn

@pytest.fixture
def indicator_script():
    # Mock export value for the indicator script
    return IndicatorScript("source_code", "export_value")

def test_indicator_script_validate(indicator_script):
    # Indicator script is always valid in this basic form
    assert indicator_script.validate()

def test_indicator_script_export(indicator_script):
    # Test the export property
    assert indicator_script.export == "export_value"  # Should return the export value