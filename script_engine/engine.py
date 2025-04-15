from typing import Any, Dict, Optional
from numpy import True_
import pandas as pd
import logging

# Import namespaces
from script_engine.namespaces.chart import ChartNamespace
from script_engine.namespaces.color import ColorNamespace
from script_engine.namespaces.input import InputNamespace
from script_engine.namespaces.strategy import StrategyNamespace
from script_engine.namespaces.ta import TANamespace

# Import core components
from .parser import ScriptParser
from .runtime import RuntimeEnvironment, ExecutionInputBase, ScriptNotFoundError # Updated import
from .script import Script, ScriptType # Keep ScriptType for potential future use if needed
from .exceptions import ScriptEngineError, ScriptRuntimeError

logger = logging.getLogger(__name__)

class ScriptEngine:
    """
    High-level interface for parsing, managing, and executing scripts
    with isolated contexts and custom imports.
    """

    def __init__(self,
                 script_sources: Dict[str, str],
                 main_script_definition_id: str,
                 column_mapping: Dict[str, str] = None,
                 inputs_override: Dict[str, Any] = None,
                 generate_output_after_run: bool = True):
        """
        Initializes the Script Engine.

        Args:
            script_sources: Dictionary mapping definition_id (e.g., path/name) to script source code string.
                            Must include the main script and all potential imports.
            main_script_definition_id: The definition_id of the script to be executed as the main entry point.
            column_mapping: Optional mapping for renaming DataFrame columns (e.g., {'Open': 'open'}).
            inputs_override: Optional dictionary to override default input values defined in scripts.
            generate_output_after_run: Whether to automatically generate namespace outputs after each run.
        """
        if not script_sources:
            raise ScriptEngineError("At least one script source must be provided.")
        if main_script_definition_id not in script_sources:
            raise ScriptEngineError(f"Main script definition ID '{main_script_definition_id}' not found in script_sources.")

        self.parser = ScriptParser()
        self.script_definitions: Dict[str, Script] = {}
        self.main_script_definition_id = main_script_definition_id

        # Parse all provided scripts
        logger.info(f"Parsing {len(script_sources)} script sources...")
        for definition_id, source in script_sources.items():
            try:
                # Pass the definition_id to the parser so it can be stored in metadata
                self.script_definitions[definition_id] = self.parser.parse(source, script_id=definition_id)
                logger.debug(f"Successfully parsed script: {definition_id}")
            except Exception as e:
                raise ScriptEngineError(f"Failed to parse script '{definition_id}': {e}") from e

        # Initialize the runtime environment with all parsed script definitions
        self.runtime = RuntimeEnvironment(
            script_definitions=self.script_definitions,
            column_mapping=column_mapping,
            generate_output_after_run=generate_output_after_run
        )

        # Initialize and register default namespaces
        self._init_default_namespaces(inputs_override)

        # Validate the main script exists after parsing
        if self.main_script_definition_id not in self.script_definitions:
             # This case should theoretically not happen due to the initial check, but good practice
             raise ScriptEngineError(f"Main script '{self.main_script_definition_id}' could not be parsed or found.")

        logger.info(f"ScriptEngine initialized. Main script: '{self.main_script_definition_id}'. Total scripts loaded: {len(self.script_definitions)}")


    def _init_default_namespaces(self, inputs_override: Optional[Dict[str, Any]]) -> None:
        """Initialize and register the default namespaces."""
        # TODO: Consider how inputs_override should interact with parsed script inputs.
        # Maybe InputNamespace needs access to the script metadata?
        # For now, it only uses the overrides provided to the engine.
        self.runtime.register_namespace("ta", TANamespace())
        self.runtime.register_namespace("input", InputNamespace(inputs_override or {}))
        self.runtime.register_namespace("chart", ChartNamespace())
        self.runtime.register_namespace("color", ColorNamespace())
        self.runtime.register_namespace("strategy", StrategyNamespace())
        logger.debug("Default namespaces registered.")

    def register_namespace(self, name: str, namespace: Any) -> None:
        """Register or override a namespace implementation."""
        logger.info(f"Registering namespace: {name}")
        self.runtime.register_namespace(name, namespace)

    def run(self, bars_df: pd.DataFrame) -> Any:
        """
        Executes one cycle (e.g., for one bar) of the main script.

        For strategies, this typically calls the process() function.
        For indicators, this might call an update() function and return the export value.
        State is maintained between calls within the RuntimeEnvironment.

        Args:
            bars_df: DataFrame with historical bar data. The runtime will extract
                     the current bar and provide access to the full history.

        Returns:
            The result of the script execution for this cycle (specifics depend
            on the script type and its implementation).
        """
        if not isinstance(bars_df, pd.DataFrame) or bars_df.empty:
            raise ScriptEngineError("Input bars_df must be a non-empty pandas DataFrame.")

        try:
            # Prepare execution input for the runtime
            # Ensure current_bar is a Series
            current_bar_series = bars_df.iloc[-1] if not bars_df.empty else None

            # Create the ExecutionInputBase object required by the new RuntimeEnvironment.run signature
            execution_input = ExecutionInputBase(
                current=current_bar_series, # This will be transformed by runtime's column mapping
                all=bars_df,                # This will be transformed by runtime's column mapping
                raw_all=bars_df             # Pass the original DataFrame as raw_all
            )

            # Execute using the runtime's run method
            logger.debug(f"Running main script '{self.main_script_definition_id}' for current bar.")
            result = self.runtime.run(
                main_script_definition_id=self.main_script_definition_id,
                execution_input=execution_input
            )
            logger.debug(f"Script execution finished. Result: {type(result)}")
            return result

        except (ScriptRuntimeError, ScriptNotFoundError) as e:
            logger.error(f"Script runtime error: {e}", exc_info=True)
            # Re-raise as ScriptEngineError or let specific runtime errors propagate?
            raise ScriptEngineError(f"Script execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during script execution: {e}", exc_info=True)
            raise ScriptEngineError(f"Unexpected script execution failed: {str(e)}") from e

    def reset_runtime(self) -> None:
        """Resets the runtime environment, clearing all state."""
        logger.info("Resetting script engine runtime state.")
        self.runtime.reset()

    def generate_outputs(self) -> Dict[str, Any]:
        """Manually generate outputs from all namespaces that support output generation.

        Returns:
            A dictionary mapping namespace names to their generated outputs.
        """
        logger.debug("Manually generating namespace outputs.")
        return self.runtime.generate_namespace_outputs()

    # Potential future methods:
    # def get_script_metadata(self, definition_id: str) -> Optional[ScriptMetadata]:
    #     script = self.script_definitions.get(definition_id)
    #     return script.metadata if script else None
    #
    # def get_context_globals(self, instance_id: str) -> Optional[Dict[str, Any]]:
    #     context = self.runtime.execution_contexts.get(instance_id)
    #     return context.globals if context else None