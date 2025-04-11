from typing import Any, Dict, Optional, Set
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
    current: pd.DataFrame
    all: pd.DataFrame
    raw_all: pd.DataFrame

class RuntimeEnvironment:
    """Manages script execution context with shared state."""
    
    def __init__(self, column_mapping: Dict[str, str]):
        self.registered_namespaces: Dict[str, Any] = {}
        self.imported_indicators: Dict[str, Any] = {}
        self.runtime_state: Optional[RuntimeState] = None
        self.column_mapping: Dict[str, str] = column_mapping
        self.shared_context: Dict[str, Any] = {}
        self.setup_executed: Set[str] = set()

    def register_namespace(self, name: str, namespace: Any) -> None:
        """Register a namespace implementation."""
        self.registered_namespaces[name] = namespace

    def execute_script(self, script: Script, execution_input: RuntimeExecutionInput) -> Any:
        """Execute a script with the provided context."""
        try:
            # Setup runtime state
            self.runtime_state = RuntimeState(
                current=self._transform_bar_column(execution_input.current_bar),
                all=self._transform_bar_column(execution_input.all_bar),
                raw_all=execution_input.all_bar
            )

            # Create execution environment
            env = self._create_execution_environment()
            
            # Inject execution-specific items
            env.update({
                'data': self.runtime_state
            })

            # Execute the script
            exec(script.source, env)
            
            # Update shared context (to include setup and process function from strategy)
            function_to_include = {'setup', 'process'}
            for key, value in env.items():
                if key in function_to_include:
                    self.shared_context[key] = value

            # Handle strategy-specific execution
            if script.metadata.type == ScriptType.STRATEGY:
                if script.id not in self.setup_executed and 'setup' in self.shared_context:
                    self.shared_context['setup']()
                    self.setup_executed.add(script.id)
                
                if 'process' in self.shared_context:
                    self.shared_context['process']()
                    
            # Update shared context (excluding injected items)
            keys_to_exclude = set(self.registered_namespaces.keys()) | {'import', 'data'}
            for key, value in env.items():
                if key not in keys_to_exclude:
                    self.shared_context[key] = value

            # Return indicator result if applicable
            return self.shared_context.get('export', None)
            
        except Exception as e:
            raise ScriptRuntimeError(f"Runtime error: {str(e)}") from e

    def _transform_bar_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform DataFrame columns according to column mapping."""
        if not self.column_mapping or not isinstance(df, pd.DataFrame):
            return df
        return df.rename(columns=self.column_mapping)

    def _create_execution_environment(self) -> Dict[str, Any]:
        """Create base execution environment with shared context and namespaces."""
        env = self.shared_context.copy()
        env.update(self.registered_namespaces)
        env["import"] = self._import_indicator
        return env

    def _import_indicator(self, name: str) -> Any:
        """Import an indicator script."""
        if name not in self.imported_indicators:
            raise ScriptRuntimeError(f"Indicator '{name}' not found")
        return self.imported_indicators[name]