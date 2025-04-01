import pytest
from script_engine.script import ScriptType

def test_execute_strategy_script(runtime, parser, valid_strategy_script):
    script = parser.parse(valid_strategy_script)
    process_func = runtime.execute_script(script)
    assert callable(process_func)
    
    # Test process function with mock bar data
    mock_bar = {"close": 100.0}
    process_func(mock_bar)  # Should not raise any errors

def test_execute_indicator_script(runtime, parser, valid_indicator_script):
    script = parser.parse(valid_indicator_script)
    result = runtime.execute_script(script, bar={"close": [90, 95, 100, 105, 110]})
    assert result is not None  # Placeholder implementation returns 0.0

def test_import_indicator(runtime, parser):
    # First register an indicator
    indicator_script = """
def calculate_sma(data, length):
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)
"""
    indicator = parser.parse(indicator_script)
    runtime.imported_indicators["sma_indicator"] = indicator
    
    # Test importing the indicator
    result = runtime._import_indicator("sma_indicator")
    assert result == indicator
    
    # Test importing non-existent indicator
    with pytest.raises(ValueError) as exc_info:
        runtime._import_indicator("non_existent")
    assert "Indicator 'non_existent' not found" in str(exc_info.value)

def test_namespace_injection(runtime):
    # Test TA namespace
    assert "ema" in runtime.namespaces["ta"]
    assert "rsi" in runtime.namespaces["ta"]
    
    # Test input namespace
    assert "int" in runtime.namespaces["input"]
    assert "float" in runtime.namespaces["input"]
    assert "text" in runtime.namespaces["input"]
    
    # Test chart namespace
    assert "plot" in runtime.namespaces["chart"]
    
    # Test color namespace
    assert "red" in runtime.namespaces["color"]
    assert "green" in runtime.namespaces["color"]
    assert "blue" in runtime.namespaces["color"]
    
    # Test strategy namespace
    assert "long" in runtime.namespaces["strategy"]
    assert "short" in runtime.namespaces["strategy"]
    assert "close" in runtime.namespaces["strategy"]
    assert "position" in runtime.namespaces["strategy"]

def test_execution_environment(runtime, parser, valid_strategy_script):
    script = parser.parse(valid_strategy_script)
    env = runtime._create_execution_environment(script)
    
    # Check if all namespaces are available
    assert "ta" in env
    assert "input" in env
    assert "chart" in env
    assert "color" in env
    assert "strategy" in env
    assert "import" in env 