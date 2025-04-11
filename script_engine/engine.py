from typing import Any, Dict, Optional
import pandas as pd

from script_engine.namespaces.chart import ChartNamespace
from script_engine.namespaces.color import ColorNamespace
from script_engine.namespaces.input import InputNamespace
from script_engine.namespaces.strategy import StrategyNamespace
from script_engine.namespaces.ta import TANamespace
from .parser import ScriptParser
from .runtime import RuntimeEnvironment, RuntimeExecutionInput
from .script import ScriptType
from .exceptions import ScriptEngineError


class ScriptEngine:
    """High-level interface for script execution."""
    
    def __init__(self, script_source: str, column_mapping: Dict[str, str] = None, inputs_override: Dict[str, Any] = None):
        self.parser = ScriptParser()
        self.script_source = script_source
        self.runtime = RuntimeEnvironment(
            column_mapping=column_mapping or {}
        )
        self._init_default_namespaces(inputs_override)
        
        # Parse script
        self.script = self.parser.parse(script_source)
        
    def _init_default_namespaces(self, inputs_override: Dict[str, Any]) -> None:
        """Initialize the default namespaces."""
        self.runtime.register_namespace("ta", TANamespace())
        self.runtime.register_namespace("input", InputNamespace(inputs_override or {}))
        self.runtime.register_namespace("chart", ChartNamespace())
        self.runtime.register_namespace("color", ColorNamespace())
        self.runtime.register_namespace("strategy", StrategyNamespace())

    def register_namespace(self, name: str, namespace: Any) -> None:
        """Register or override a namespace."""
        self.runtime.register_namespace(name, namespace)

    def run_script(
        self,
        bars_df: pd.DataFrame,
        script_type: ScriptType = None
    ) -> Any:
        """
        Execute a script (strategy or indicator) and return its result.
        
        Args:
            bars_df: DataFrame with historical bar data including current bar
            script_type: The type of the script (e.g. ScriptType.STRATEGY or ScriptType.INDICATOR)
        
        Returns:
            The result of executing the script
        """
        try:
            if self.script.metadata.type != script_type:
                raise ScriptEngineError(f"Only {script_type} scripts can be executed with run_script().")

            return self.runtime.execute_script(
                self.script,
                execution_input=RuntimeExecutionInput(
                    current_bar=bars_df.iloc[-1],  # Last row as DataFrame
                    all_bar=bars_df       # All except last row
                )
            )
        except Exception as e:
            raise ScriptEngineError(f"Script execution failed: {str(e)}") from e