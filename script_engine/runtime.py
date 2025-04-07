from typing import Any, Dict, Optional
import pandas as pd
from dataclasses import dataclass
from .script import Script, ScriptType
from .exceptions import ScriptRuntimeError

@dataclass
class RuntimeExecutionInput:
    current_bar: pd.DataFrame
    all_bar: pd.DataFrame

@dataclass
class RuntimeState:
    """Tracks execution context and data."""
    current_bar: pd.DataFrame # Only contains items for a single row
    all_bar: pd.DataFrame # NOTE: This data should not contain current_bar when doing backtesting to avoid look-ahead bias
    raw_all_bar: pd.DataFrame
    

class RuntimeEnvironment:
    """Manages script execution context and namespaces."""
    
    def __init__(self, column_mapping: Dict[str, str], inputs_override: Dict[str, Any] = {}):
        self.registered_namespaces: Dict[str, Any] = {}
        self.imported_indicators: Dict[str, Any] = {}
        self.runtime_state: Optional[RuntimeState] = None
        self.column_mapping: Dict[str, str] = column_mapping
        self.inputs: Dict[str, Any] = inputs_override

    def register_namespace(self, name: str, namespace: Any) -> None:
        """Register a namespace implementation."""
        self.registered_namespaces[name] = namespace

    def execute_script(self, script: Script, execution_input: RuntimeExecutionInput) -> Any:
        """Execute a script with the provided context."""
        try:
            # Setup runtime state
            self.runtime_state = RuntimeState(
                current_bar=self._transform_bar_column(execution_input.current_bar),
                all_bar=self._transform_bar_column(execution_input.all_bar),
                raw_all_bar=execution_input.all_bar
            )

            # Create execution environment with namespaces
            env = self._create_execution_environment()
            
            if script.metadata.type == ScriptType.STRATEGY:
                return self._execute_strategy(script, env)
            return self._execute_indicator(script, env)
                
        except Exception as e:
            raise ScriptRuntimeError(f"Runtime error: {str(e)}") from e
    
    def _transform_bar_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform DataFrame columns according to column mapping.
        
        Args:
            df: Input dataframe containing bar data
            
        Returns:
            DataFrame with columns renamed according to column_mapping
        """
        if not self.column_mapping or not isinstance(df, pd.DataFrame):
            return df
            
        # Rename columns according to column_mapping
        return df.rename(columns=self.column_mapping)

    def _create_execution_environment(self) -> Dict[str, Any]:
        """Create script execution environment with registered namespaces."""
        env = {
            **self.registered_namespaces,
            "import": self._import_indicator
        }
        return env

    def _execute_strategy(self, script: Script, env: Dict[str, Any]) -> Any:
        """Execute strategy script."""
        if hasattr(script, "setup"):
            script.setup(**env)
        return script.process

    def _execute_indicator(self, script: Script, env: Dict[str, Any]) -> Any:
        """Execute indicator script."""
        exec(script.source, env)
        return env.get("export")

    def _import_indicator(self, name: str) -> Any:
        """Import an indicator script."""
        if name not in self.imported_indicators:
            raise ScriptRuntimeError(f"Indicator '{name}' not found")
        return self.imported_indicators[name]