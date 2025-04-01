from typing import Any, Dict, Optional
from .script import Script, ScriptType, ScriptMetadata

class RuntimeEnvironment:
    def __init__(self):
        self.namespaces = {
            "ta": self._create_ta_namespace(),
            "input": self._create_input_namespace(),
            "chart": self._create_chart_namespace(),
            "color": self._create_color_namespace(),
            "strategy": self._create_strategy_namespace()
        }
        self.imported_indicators: Dict[str, Any] = {}
        
    def execute_script(self, script: Script, **kwargs) -> Any:
        """Execute a script with the given parameters."""
        # Create execution environment
        env = self._create_execution_environment(script, **kwargs)
        
        # Execute based on script type
        if script.metadata.type == ScriptType.STRATEGY:
            return self._execute_strategy_script(script, env)
        else:
            return self._execute_indicator_script(script, env)
            
    def _create_execution_environment(self, script: Script, **kwargs) -> Dict[str, Any]:
        """Create the execution environment with all necessary namespaces and variables."""
        env = {
            **self.namespaces,
            "import": self._import_indicator,
            **kwargs
        }
        return env
        
    def _execute_strategy_script(self, script: Script, env: Dict[str, Any]) -> None:
        """Execute a strategy script."""
        # First execute setup
        if hasattr(script, "setup"):
            script.setup(**env)
            
        # Return the process function for later execution on each bar
        return script.process
        
    def _execute_indicator_script(self, script: Script, env: Dict[str, Any]) -> Any:
        """Execute an indicator script and return its export value."""
        # Execute the script in the environment
        exec(script.source, env)
        
        # Return the export value
        return env.get("export")
        
    def _import_indicator(self, name: str) -> Any:
        """Import an indicator script by name."""
        if name not in self.imported_indicators:
            raise ValueError(f"Indicator '{name}' not found")
        return self.imported_indicators[name]
        
    def _create_ta_namespace(self) -> Dict[str, Any]:
        """Create the technical analysis namespace."""
        return {
            "ema": lambda src, length: 0.0,  # Placeholder
            "rsi": lambda src, length: 0.0,  # Placeholder
            # Add more TA functions as needed
        }
        
    def _create_input_namespace(self) -> Dict[str, Any]:
        """Create the input namespace."""
        return {
            "int": lambda name, **kwargs: 0,  # Placeholder
            "float": lambda name, **kwargs: 0.0,  # Placeholder
            "text": lambda name, **kwargs: "",  # Placeholder
            # Add more input types as needed
        }
        
    def _create_chart_namespace(self) -> Dict[str, Any]:
        """Create the chart namespace."""
        return {
            "plot": lambda value, **kwargs: None,  # Placeholder
            # Add more chart functions as needed
        }
        
    def _create_color_namespace(self) -> Dict[str, Any]:
        """Create the color namespace."""
        return {
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF",
            # Add more colors as needed
        }
        
    def _create_strategy_namespace(self) -> Dict[str, Any]:
        """Create the strategy namespace."""
        return {
            "long": lambda **kwargs: None,  # Placeholder
            "short": lambda **kwargs: None,  # Placeholder
            "close": lambda **kwargs: None,  # Placeholder
            "position": lambda **kwargs: None,  # Placeholder
            # Add more strategy functions as needed
        } 