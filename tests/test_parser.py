import pytest
from script_engine.exceptions.parsing_specific import MissingScriptTypeError
from script_engine.script import ScriptType

def test_parse_valid_strategy(parser, valid_strategy_script):
    script = parser.parse(valid_strategy_script)
    assert script.metadata.type == ScriptType.STRATEGY
    # assert "length" in script.metadata.inputs
    # assert len(script.metadata.exports) == 0
    # assert len(script.metadata.imports) == 0

def test_parse_valid_indicator(parser, valid_indicator_script):
    script = parser.parse(valid_indicator_script)
    assert script.metadata.type == ScriptType.INDICATOR
    # assert len(script.metadata.inputs) == 0
    # assert "export" in script.metadata.exports
    # assert len(script.metadata.imports) == 0

def test_parse_invalid_strategy(parser, invalid_strategy_script):
    from script_engine.exceptions.parsing_specific import InvalidInputUsageError
    with pytest.raises(InvalidInputUsageError) as exc_info:
        parser.parse(invalid_strategy_script)

def test_parse_invalid_indicator(parser, invalid_indicator_script):
    from script_engine.exceptions.parsing_specific import MultipleExportsError
    with pytest.raises(MultipleExportsError) as exc_info:
        parser.parse(invalid_indicator_script)

def test_parse_syntax_error(parser):
    invalid_syntax = """
def setup()
    return {}
"""
    from script_engine.exceptions.parsing import ScriptParsingError
    with pytest.raises(ScriptParsingError) as exc_info:
        parser.parse(invalid_syntax)

def test_parse_missing_required_functions(parser):
    invalid_strategy = """
def setup():
    return {}
"""
    from script_engine.exceptions.parsing_specific import MissingScriptTypeError
    with pytest.raises(MissingScriptTypeError) as exc_info:
        parser.parse(invalid_strategy)
        
def test_When_IndicatorExportMissing_Expect_MissingScriptTypeError(runtime, parser):
    with pytest.raises(MissingScriptTypeError):
        script = parser.parse("""
def calculate():
    return 1
# Missing export statement
""")
        runtime.execute_script(script)

def test_parse_strategy_with_indicator_import(parser):
    script_with_import = """
def setup():
    import sma_indicator

def process(bar):
    if sma_indicator > bar.close:
        strategy.long()
"""
    script = parser.parse(script_with_import)
    assert script.metadata.type == ScriptType.STRATEGY
    assert "sma_indicator" in script.metadata.imports

def test_When_IndicatorUsesStrategyFunction_Expect_ValueError(parser):
    invalid_indicator_with_strategy_call = """
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)

def dummy():
    strategy.long()
"""
    from script_engine.exceptions.parsing_specific import StrategyFunctionInIndicatorError
    with pytest.raises(StrategyFunctionInIndicatorError) as exc_info:
        parser.parse(invalid_indicator_with_strategy_call)