import pandas as pd
from typing import Any, Dict, Optional, Set, Callable
from dataclasses import dataclass, field
import uuid
import copy
import logging

# Assuming Script and ScriptType are imported from the updated script.py
from .script import Script, ScriptType
from .exceptions import ScriptRuntimeError, ScriptNotFoundError

logger = logging.getLogger(__name__)

# Removed RuntimeExecutionInput - The user will pass an instance of ExecutionInputBase directly to run()

@dataclass
class ExecutionInputBase:
    """Base class for data provided to the script execution context."""
    current: Optional[pd.Series] = None
    all: Optional[pd.DataFrame] = None
    raw_all: Optional[pd.DataFrame] = None

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return None

    def __deepcopy__(self, memo):
        """Properly implement deep copy for the class."""
        return ExecutionInputBase(
            current=copy.deepcopy(self.current, memo) if self.current is not None else None,
            all=copy.deepcopy(self.all, memo) if self.all is not None else None,
            raw_all=copy.deepcopy(self.raw_all, memo) if self.raw_all is not None else None
        )

@dataclass
class ExecutionContext:
    """Holds the state and globals for a single script instance."""
    instance_id: str
    definition_id: str # ID of the script definition (e.g., path)
    globals: Dict[str, Any] = field(default_factory=dict)
    # Add specific state management if needed beyond globals
    # e.g., setup_executed: bool = False
    # e.g., internal_state: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Basic builtins, can be customized further
        self.globals['__builtins__'] = {
            'print': print,
            'len': len,
            'range': range,
            'abs': abs,
            'round': round,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            # Add other safe builtins as needed
        }
        # Prevent access to potentially harmful builtins
        self.globals['__builtins__']['eval'] = None
        self.globals['__builtins__']['exec'] = None
        self.globals['__builtins__']['open'] = None
        self.globals['__builtins__']['compile'] = None
        self.globals['__builtins__']['input'] = None
        self.globals['__builtins__']['__import__'] = None


# Removed RuntimeState dataclass, replaced by direct use of ExecutionInputBase instance
class RuntimeEnvironment:
    """Manages isolated execution contexts for scripts."""

    def __init__(self,
                 script_definitions: Dict[str, Script],
                 column_mapping: Dict[str, str] = None):
        """
        Initializes the runtime environment.

        Args:
            script_definitions: A dictionary mapping definition_id (e.g., path) to Script objects.
            column_mapping: Optional mapping for renaming DataFrame columns.
        """
        self.script_definitions: Dict[str, Script] = script_definitions
        self.column_mapping: Dict[str, str] = column_mapping or {}
        self.registered_namespaces: Dict[str, Any] = {} # Standard namespaces like 'ta', 'strategy'
        self.execution_contexts: Dict[str, ExecutionContext] = {} # instance_id -> context
        self._current_run_data: Optional[ExecutionInputBase] = None # Holds processed data during a run() call
        self._setup_executed: Set[str] = set() # Tracks instance_ids where setup ran

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
        base_globals['import_script'] = self._create_importer(context_instance_id)
        # Inject other runtime utilities if needed
        return base_globals

    def _create_importer(self, importer_instance_id: str) -> Callable[[str], Any]:
        """Creates a closure for the import_script function specific to the importing context."""
        def _importer(script_definition_id_to_import: str) -> Any:
            return self._custom_import(importer_instance_id, script_definition_id_to_import)
        return _importer

    def _custom_import(self, importer_instance_id: str, script_definition_id_to_import: str) -> Any:
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

        if instance_id in self.execution_contexts:
            # Instance already exists (e.g., multiple imports within the same caller)
            # Return its exports or context representation
            imported_context = self.execution_contexts[instance_id]
            # Decide what to return: the whole globals dict, or specific exports?
            # Returning a proxy object exposing only exported variables is safer.
            return self._get_exports_proxy(imported_context)
        else:
            # Create a new instance
            logger.debug(f"Creating new instance '{instance_id}' for script '{script_definition_id_to_import}' imported by '{importer_instance_id}'")
            script_def = self._get_script_definition(script_definition_id_to_import)

            if script_def.type == ScriptType.STRATEGY:
                raise ScriptRuntimeError(f"Cannot import a Strategy script ('{script_definition_id_to_import}'). Only Indicator scripts can be imported.")

            new_context = ExecutionContext(instance_id=instance_id, definition_id=script_definition_id_to_import)
            new_context.globals.update(self._create_base_globals(instance_id))

            # Inject current script execution data (passed to run() and processed) if available
            if self._current_run_data:
                # Inject the processed data object available during this run() call
                new_context.globals['data'] = self._current_run_data
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
            self.execution_contexts[instance_id] = new_context

            # Handle setup for the newly imported indicator if needed (Pine Script doesn't really have setup for indicators)
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
        For now, let's return the main export variable 'export' if it exists,
        similar to Pine Script's single export for indicators.
        Alternatively, could return an object with attributes for all exported vars.
        """
        # PineScript indicators typically have one primary output value.
        # Let's assume the script assigns its main result to a variable named 'export'.
        script_def = self._get_script_definition(context.definition_id) # Get definition for metadata
        if 'export' in context.globals:
             return context.globals['export']
        # Check metadata if multiple exports are explicitly defined (optional feature)
        elif script_def.metadata.exports:
             exports_dict = {k: context.globals[k] for k in script_def.metadata.exports if k in context.globals}
             # SimpleNamespace might be good if multiple exports are common
             # import types
             # return types.SimpleNamespace(**exports_dict)
             if len(exports_dict) == 1:
                 return next(iter(exports_dict.values())) # Return single value if only one export found
             elif len(exports_dict) > 1:
                 logger.warning(f"Script '{context.definition_id}' has multiple exports defined ({script_def.metadata.exports}) but no single 'export' variable. Returning dictionary of exports.")
                 return exports_dict # Return dict if multiple exports found
             else:
                 logger.warning(f"Script '{context.definition_id}' defined exports ({script_def.metadata.exports}) but none were found in the execution context.")
                 return None
        else:
            logger.warning(f"Imported script instance '{context.instance_id}' (from '{context.definition_id}') does not define an 'export' variable or specify exports in metadata.")
            return None # Or raise an error, depending on desired strictness

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
        main_instance_id = f"main::{main_script_definition_id}" # Unique ID for the main script instance

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
            main_context.globals['data'] = self._current_run_data # Inject the processed data object

            result = None
            try:
                if main_script_def.type == ScriptType.STRATEGY:
                    # Execute setup() once per instance
                    if main_instance_id not in self._setup_executed:
                        if 'setup' in main_context.globals and callable(main_context.globals['setup']):
                            logger.debug(f"Calling setup() for instance '{main_instance_id}'")
                            main_context.globals['setup']()
                            self._setup_executed.add(main_instance_id)
                        else:
                            raise ScriptRuntimeError(f"Strategy script '{main_script_definition_id}' does not have a setup() function.")

                    # Execute process() on each run
                    if 'process' in main_context.globals and callable(main_context.globals['process']):
                        logger.debug(f"Calling process() for instance '{main_instance_id}'")
                        # Pass bar explicitly if the signature requires it, otherwise assume it uses 'data'
                        # This depends on the exact function signature convention
                        # E.g., if process() takes the bar: result = main_context.globals['process'](execution_input.current_bar)
                        # Assuming process uses the 'data' global for now
                        result = main_context.globals['process']()
                    else:
                        raise ScriptRuntimeError(f"Strategy script '{main_script_definition_id}' must define a process() function.")

                elif main_script_def.type == ScriptType.INDICATOR:
                     # For an indicator run as the main script, we might just expect it to calculate
                     # and assign to 'export' during the initial exec.
                     # Or, if it needs per-bar updates, call a conventional function like 'update()' or 'calc()'.
                     if 'update' in main_context.globals and callable(main_context.globals['update']):
                         logger.debug(f"Calling update() for indicator instance '{main_instance_id}'")
                         main_context.globals['update']() # Assuming it uses 'data' global

                     # The result is the exported value after execution/update
                     result = self._get_exports_proxy(main_context)

            except Exception as e:
                # Catch errors during setup/process/update calls
                raise ScriptRuntimeError(f"Runtime error during execution of script '{main_script_definition_id}' (instance: {main_instance_id}): {str(e)}") from e
        finally:
            # --- Cleanup after Run ---
            # Ensure the temporary run data is cleared after execution finishes or fails
            self._current_run_data = None

        # Persist state: The state is implicitly persisted in the main_context.globals dictionary
        # stored in self.execution_contexts.

        return result

    def reset(self) -> None:
        """Clears all execution contexts and state."""
        logger.info("Resetting RuntimeEnvironment.")
        self.execution_contexts.clear()
        self._current_run_data = None # Clear any lingering run data
        self._setup_executed.clear()
