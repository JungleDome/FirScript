"""
Module for script importing functionality used by the script engine runtime.
"""
import logging
import uuid
from typing import Any, Callable, Dict
from types import SimpleNamespace

from .execution_context import ExecutionContext
from .exceptions import ScriptRuntimeError, ScriptNotFoundError
from .script import Script, ScriptType

logger = logging.getLogger(__name__)


class ScriptImporter:
    """Handles importing scripts within the runtime environment."""

    def __init__(self, runtime_environment):
        """
        Initialize the script importer.

        Args:
            runtime_environment: The parent RuntimeEnvironment instance
        """
        self.runtime_environment = runtime_environment

    def create_importer(self, importer_instance_id: str) -> Callable[[str], Any]:
        """
        Creates a closure for the import_script function specific to the importing context.

        Args:
            importer_instance_id: The instance ID of the script performing the import

        Returns:
            A callable that can be used to import scripts
        """
        def _importer(script_definition_id_to_import: str) -> Any:
            return self.import_script(importer_instance_id, script_definition_id_to_import)
        return _importer

    def import_script(self, importer_instance_id: str, script_definition_id_to_import: str) -> Any:
        """
        Handles the import of a script, creating an isolated instance.

        Args:
            importer_instance_id: The instance ID of the script performing the import.
            script_definition_id_to_import: The definition ID (e.g., path) of the script to import.

        Returns:
            An object representing the imported script's exports.
        """
        # Generate a unique ID for this specific instance of the imported script
        # This ensures that importing 'yyy' from 'main' and 'xxx' results in different instances
        instance_id = f"{importer_instance_id}::{script_definition_id_to_import}::{uuid.uuid4().hex[:8]}"

        if instance_id in self.runtime_environment.execution_contexts:
            # Instance already exists (e.g., multiple imports within the same caller)
            # Return its exports or context representation
            imported_context = self.runtime_environment.execution_contexts[instance_id]
            # Return a proxy object exposing only exported variables
            return self._get_exports_proxy(imported_context)
        else:
            # Create a new instance
            logger.debug(f"Creating new instance '{instance_id}' for script '{script_definition_id_to_import}' imported by '{importer_instance_id}'")
            script_def = self.runtime_environment._get_script_definition(script_definition_id_to_import)

            if script_def.type == ScriptType.STRATEGY:
                raise ScriptRuntimeError(f"Cannot import a Strategy script ('{script_definition_id_to_import}'). Only Indicator scripts can be imported.")

            new_context = ExecutionContext(instance_id=instance_id, definition_id=script_definition_id_to_import)
            new_context.globals.update(self.runtime_environment._create_base_globals(instance_id))

            # Inject current script execution data (passed to run() and processed) if available
            if self.runtime_environment._current_run_data:
                # Inject the processed data object available during this run() call
                new_context.globals['data'] = self.runtime_environment._current_run_data
            else:
                # This case should ideally not happen if import is called during a run
                logger.warning(f"No current run data available when importing '{script_definition_id_to_import}' for instance '{instance_id}'. 'data' namespace will be None.")
                new_context.globals['data'] = None

            # Execute the script code within the new context's globals
            try:
                exec(script_def.source, new_context.globals)
            except Exception as e:
                raise ScriptRuntimeError(f"Error executing imported script '{script_definition_id_to_import}' (instance: {instance_id}): {e}") from e

            # Store the new context
            self.runtime_environment.execution_contexts[instance_id] = new_context

            # Handle setup for the newly imported indicator if needed
            # If indicators need initialization, call a conventional function like 'init()' if present.
            if 'init' in new_context.globals and callable(new_context.globals['init']):
                try:
                    logger.debug(f"Calling init() for instance '{instance_id}'")
                    new_context.globals['init']()
                except Exception as e:
                    raise ScriptRuntimeError(f"Error calling init() on imported script '{script_definition_id_to_import}' (instance: {instance_id}): {e}") from e

            # Return a representation of the imported script's exports
            return self._get_exports_proxy(new_context)

    def _get_exports_proxy(self, context: ExecutionContext) -> Any:
        """
        Creates a proxy object exposing only the intended exports from a context.
        Automatically converts dictionary exports to dot-notation accessible objects.

        Args:
            context: The execution context to extract exports from

        Returns:
            The exported value(s) from the script with dot notation access
        """
        # Get script definition for metadata
        script_def = self.runtime_environment._get_script_definition(context.definition_id)

        # Get the export value
        if 'export' in context.globals:
            export_value = context.globals['export']
            # If export is a dictionary, convert it to SimpleNamespace for dot notation
            if isinstance(export_value, dict):
                return SimpleNamespace(**export_value)
            return export_value
        # Check metadata if multiple exports are explicitly defined
        elif script_def.metadata.exports:
            exports_dict = {k: context.globals[k] for k in script_def.metadata.exports if k in context.globals}
            # Return single value if only one export found
            if len(exports_dict) == 1:
                return next(iter(exports_dict.values()))
            # Convert dict to SimpleNamespace if multiple exports found
            elif len(exports_dict) > 1:
                logger.warning(f"Script '{context.definition_id}' has multiple exports defined ({script_def.metadata.exports}) but no single 'export' variable. Converting dictionary to dot notation accessible object.")
                return SimpleNamespace(**exports_dict)
            else:
                logger.warning(f"Script '{context.definition_id}' defined exports ({script_def.metadata.exports}) but none were found in the execution context.")
                return None
        else:
            logger.warning(f"Imported script instance '{context.instance_id}' (from '{context.definition_id}') does not define an 'export' variable or specify exports in metadata.")
            return None

