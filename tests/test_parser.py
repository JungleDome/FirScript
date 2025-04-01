import pytest
from script_engine.script import ScriptType

def test_parse_valid_strategy(parser, valid_strategy_script):
    script = parser.parse(valid_strategy_script)
    assert script.metadata.type == ScriptType.STRATEGY
    assert "length" in script.metadata.inputs
    assert len(script.metadata.exports) == 0
    assert len(script.metadata.imports) == 0

def test_parse_valid_indicator(parser, valid_indicator_script):
    script = parser.parse(valid_indicator_script)
    assert script.metadata.type == ScriptType.INDICATOR
    assert len(script.metadata.inputs) == 0
    assert "export" in script.metadata.exports
    assert len(script.metadata.imports) == 0

def test_parse_invalid_strategy(parser, invalid_strategy_script):
    with pytest.raises(ValueError) as exc_info:
        parser.parse(invalid_strategy_script)
    assert "Input functions cannot be used inside process()" in str(exc_info.value)

def test_parse_invalid_indicator(parser, invalid_indicator_script):
    with pytest.raises(ValueError) as exc_info:
        parser.parse(invalid_indicator_script)
    assert "Indicator script must have exactly one export" in str(exc_info.value)

def test_parse_syntax_error(parser):
    invalid_syntax = """
def setup()
    return {}
"""
    with pytest.raises(ValueError) as exc_info:
        parser.parse(invalid_syntax)
    assert "Invalid script syntax" in str(exc_info.value)

def test_parse_missing_required_functions(parser):
    invalid_strategy = """
def setup():
    return {}
"""
    with pytest.raises(ValueError) as exc_info:
        parser.parse(invalid_strategy)
    assert "Strategy script missing required functions" in str(exc_info.value)

def test_parse_strategy_with_indicator_import(parser):
    script_with_import = """
def setup():
    sma = import 'sma_indicator'
    return {"sma": sma}

def process(bar):
    if sma > bar.close:
        strategy.long()
"""
    script = parser.parse(script_with_import)
    assert script.metadata.type == ScriptType.STRATEGY
    assert "sma_indicator" in script.metadata.imports 