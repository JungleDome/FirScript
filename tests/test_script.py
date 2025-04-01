import pytest
from script_engine.script import Script, ScriptType, ScriptMetadata

class TestScript(Script):
    def validate(self) -> bool:
        return True
        
    def extract_metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="test",
            type=ScriptType.STRATEGY,
            inputs={},
            exports=set(),
            imports=[]
        )

def test_script_initialization():
    source = "def setup(): pass"
    script = TestScript(source)
    assert script.source == source
    assert script.metadata is None

def test_script_setup():
    script = TestScript("")
    script.setup()  # Should not raise any errors

def test_script_process():
    script = TestScript("")
    script.process({"close": 100.0})  # Should not raise any errors

def test_script_export():
    script = TestScript("")
    with pytest.raises(NotImplementedError):
        _ = script.export

def test_script_metadata():
    script = TestScript("")
    metadata = script.extract_metadata()
    assert isinstance(metadata, ScriptMetadata)
    assert metadata.name == "test"
    assert metadata.type == ScriptType.STRATEGY
    assert isinstance(metadata.inputs, dict)
    assert isinstance(metadata.exports, set)
    assert isinstance(metadata.imports, list) 