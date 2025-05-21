from typing import Any, override
import pandas as pd

from firscript.engine import Engine
from firscript.namespaces.base import BaseNamespace


def test_When_EngineInitialized_Expect_CanRegisterNewNamespace():
    class CustomNamespace(BaseNamespace):
        """Custom namespace for testing."""

        def __init__(self, shared: dict[str, Any]):
            super().__init__(shared)
            self.text = ""

        def custom_function(self):
            self.text = "Hello, World!"

        @override
        def generate_output(self):
            return {"custom_output": self.text}

    script = """
def setup():
    pass

def process():
    custom.custom_function()
"""

    engine = Engine()
    engine.register_default_namespaces()
    engine.register_import_script_namespace()
    engine.register_scripts(main_script=script)
    engine.registry.register("custom", CustomNamespace(engine.registry.shared))
    engine.initialize_context()
    result, metadata = engine.run(pd.DataFrame({"timestamp": pd.date_range(
        "2023-01-01", periods=10)}))
    assert "custom" in engine.registry.namespaces
    assert result["custom"]["custom_output"] == "Hello, World!"
