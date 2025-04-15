"""
Module for the runtime environment used by the script engine.
"""
import copy
import logging
from typing import Any, Dict, Optional, Set

import pandas as pd

from .execution_context import ExecutionContext
from .execution_input import ExecutionInputBase
from .exceptions import ScriptRuntimeError, ScriptNotFoundError
from .script import Script, ScriptType
from .script_importer import ScriptImporter
from .namespaces.base import BaseNamespace

logger = logging.getLogger(__name__)


class RuntimeEnvironment:
    """Manages isolated execution contexts for scripts."""

    def __init__(self,
                 script_definitions: Dict[str, Script],
                 column_mapping: Dict[str, str] = None,
                 generate_output_after_run: bool = True):
        """
        Initializes the runtime environment.

        Args:
            script_definitions: A dictionary mapping definition_id (e.g., path) to Script objects.
            column_mapping: Optional mapping for renaming DataFrame columns.
            generate_output_after_run: Whether to automatically generate namespace outputs after each run.
        """
        self.script_definitions: Dict[str, Script] = script_definitions
        self.column_mapping: Dict[str, str] = column_mapping or {}
        self.registered_namespaces: Dict[str, Any] = {}  # Standard namespaces like 'ta', 'strategy'
        self.execution_contexts: Dict[str, ExecutionContext] = {}  # instance_id -> context
        self._current_run_data: Optional[ExecutionInputBase] = None  # Holds processed data during a run() call
        self._setup_executed: Set[str] = set()  # Tracks instance_ids where setup ran
        self.generate_output_after_run: bool = generate_output_after_run

        # Initialize the script importer
        self.script_importer = ScriptImporter(self)

    def register_namespace(self, name: str, namespace_obj: Any) -> None:
        """Registers a standard namespace available to all scripts."""
        self.registered_namespaces[name] = namespace_obj

    def _get_script_definition(self, definition_id: str) -> Script:
        """Retrieves a script definition by its ID."""
        script = self.script_definitions.get(definition_id)
        if not script:
            raise ScriptNotFoundError(f"Script definition '{definition_id}' not found.")
        return script

    def _transform_bar_data(self, df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """Transforms DataFrame columns according to column mapping."""
        if df is None or df.empty or not self.column_mapping:
            return df
        return df.rename(columns=self.column_mapping)

    def _create_base_globals(self, context_instance_id: str) -> Dict[str, Any]:
        """Creates the base global dictionary for a new execution context."""
        base_globals = {}
        # Inject standard namespaces
        base_globals.update(self.registered_namespaces)
        # Inject the custom import function, bound to the current context
        base_globals['import_script'] = self.script_importer.create_importer(context_instance_id)
        # Inject other runtime utilities if needed
        return base_globals

    def run(self, main_script_definition_id: str, execution_input: ExecutionInputBase) -> Any:
        """
        Executes the main script and handles its lifecycle (setup, process).

        Args:
            main_script_definition_id: The definition ID (e.g., path) of the main script to run.
            execution_input: An instance of ExecutionInputBase (or a subclass) containing
                             current, all, raw_all, and any other custom data needed for the script.
                             The 'current' and 'all' fields will be transformed internally based
                             on the column_mapping. The original object passed by the caller
                             will NOT be modified.

        Returns:
            The result of the execution (e.g., indicator value, strategy signals).
        """
        main_script_def = self._get_script_definition(main_script_definition_id)
        main_instance_id = f"main::{main_script_definition_id}"  # Unique ID for the main script instance

        # --- Prepare Data for this Run ---
        try:
            # Deep copy the input to prevent modifying the caller's object and
            # to allow safe internal transformation (column mapping).
            processed_data = copy.deepcopy(execution_input)

            # Apply column mapping to the copied data's 'current' and 'all' fields
            if processed_data.current is not None:
                processed_data.current = self._transform_bar_data(processed_data.current)
            if processed_data.all is not None:
                processed_data.all = self._transform_bar_data(processed_data.all)
            # Note: raw_all remains untransformed by design.

            # Store the processed data temporarily for access during this run (e.g., by imports)
            self._current_run_data = processed_data

            # Get or create the main execution context
            if main_instance_id not in self.execution_contexts:
                logger.debug(f"Creating main context for instance '{main_instance_id}'")
                main_context = ExecutionContext(instance_id=main_instance_id, definition_id=main_script_definition_id)
                main_context.globals.update(self._create_base_globals(main_instance_id))
                # Execute the main script source code *once* to define functions etc.
                try:
                    exec(main_script_def.source, main_context.globals)
                except Exception as e:
                    raise ScriptRuntimeError(f"Error during initial execution of main script '{main_script_definition_id}': {e}") from e
                self.execution_contexts[main_instance_id] = main_context
            else:
                main_context = self.execution_contexts[main_instance_id]

            # --- Lifecycle Execution ---

            # Inject current data into the main context for this run
            main_context.globals['data'] = self._current_run_data  # Inject the processed data object

            # Variable to store the result from library scripts
            result = None

            try:
                if main_script_def.type == ScriptType.STRATEGY:
                    self._run_strategy(main_instance_id, main_context)
                elif main_script_def.type == ScriptType.INDICATOR:
                    self._run_indicator(main_instance_id, main_context)
                elif main_script_def.type == ScriptType.LIBRARY:
                    result = self._run_library(main_instance_id, main_context)
                else:
                    raise ScriptRuntimeError(f"Unknown script type: {main_script_def.type}")
            except Exception as e:
                # Catch errors during setup/process/update calls
                raise ScriptRuntimeError(f"Runtime error during execution of script '{main_script_definition_id}' (instance: {main_instance_id}): {str(e)}") from e
        finally:
            # --- Cleanup after Run ---
            # Ensure the temporary run data is cleared after execution finishes or fails
            self._current_run_data = None

        # Persist state: The state is implicitly persisted in the main_context.globals dictionary
        # stored in self.execution_contexts.

        # For library scripts, return the export value
        if main_script_def.type == ScriptType.LIBRARY and result is not None:
            return result

        # Generate outputs from namespaces if configured
        if self.generate_output_after_run:
            namespace_outputs = self.generate_namespace_outputs()
            if namespace_outputs:
                return namespace_outputs

        # Return None if no namespace outputs are generated and not a library script
        return None

    def _run_strategy(self, instance_id: str, context: ExecutionContext) -> None:
        """
        Run a strategy script.

        Args:
            instance_id: The instance ID of the strategy
            context: The execution context for the strategy
        """
        # Execute setup() once per instance
        if instance_id not in self._setup_executed:
            if 'setup' in context.globals and callable(context.globals['setup']):
                logger.debug(f"Calling setup() for instance '{instance_id}'")
                context.globals['setup']()
                self._setup_executed.add(instance_id)
            else:
                raise ScriptRuntimeError(f"Strategy script '{context.definition_id}' does not have a setup() function.")

        # Execute process() on each run
        if 'process' in context.globals and callable(context.globals['process']):
            logger.debug(f"Calling process() for instance '{instance_id}'")
            # Assuming process uses the 'data' global
            context.globals['process']()
        else:
            raise ScriptRuntimeError(f"Strategy script '{context.definition_id}' must define a process() function.")

    def _run_indicator(self, instance_id: str, context: ExecutionContext) -> None:
        """
        Run an indicator script.

        Args:
            instance_id: The instance ID of the indicator
            context: The execution context for the indicator
        """
        # Execute setup() once per instance (same as strategy)
        if instance_id not in self._setup_executed:
            if 'setup' in context.globals and callable(context.globals['setup']):
                logger.debug(f"Calling setup() for indicator instance '{instance_id}'")
                context.globals['setup']()
                self._setup_executed.add(instance_id)
            else:
                raise ScriptRuntimeError(f"Indicator script '{context.definition_id}' does not have a setup() function.")

        # Execute process() on each run (same as strategy)
        if 'process' in context.globals and callable(context.globals['process']):
            logger.debug(f"Calling process() for indicator instance '{instance_id}'")
            context.globals['process']()
        else:
            raise ScriptRuntimeError(f"Indicator script '{context.definition_id}' must define a process() function.")

    def _run_library(self, instance_id: str, context: ExecutionContext) -> Any:
        """
        Run a library script.

        Args:
            instance_id: The instance ID of the library
            context: The execution context for the library

        Returns:
            The value of the export variable
        """
        # Library scripts are primarily used for importing, so we don't need to execute any functions
        # The export variable should already be defined during the initial exec
        logger.debug(f"Running library script instance '{instance_id}'")

        # Return the export variable
        if 'export' in context.globals:
            return context.globals['export']
        else:
            raise ScriptRuntimeError(f"Library script '{context.definition_id}' does not have an export variable.")

    def generate_namespace_outputs(self) -> Dict[str, Any]:
        """
        Generate outputs from all namespaces that support output generation.

        Returns:
            A dictionary mapping namespace names to their generated outputs.
        """
        outputs = {}
        for name, namespace in self.registered_namespaces.items():
            if isinstance(namespace, BaseNamespace):
                output = namespace.generate_output()
                if output is not None:
                    outputs[name] = output
        return outputs

    def reset(self) -> None:
        """Clears all execution contexts and state."""
        logger.info("Resetting RuntimeEnvironment.")
        self.execution_contexts.clear()
        self._current_run_data = None  # Clear any lingering run data
        self._setup_executed.clear()
