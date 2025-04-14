import ast
from typing import Any, Dict, List, Set, Tuple # Added Dict
from typing import List, Set, Tuple

from script_engine.exceptions.parsing_specific import StrategyGlobalVariableError
from .script import Script, ScriptType, ScriptMetadata

class ScriptParser:
    def __init__(self):
        self.required_strategy_functions = {"setup", "process"}
        self.allowed_namespaces = {"ta", "input", "chart", "color", "strategy"}
        
    def parse(self, source: str, script_id: str) -> Script:
        """Parse and validate a script source."""
        try:
            tree = ast.parse(source)
            script_type = self._determine_script_type(tree)
            
            # Extract metadata
            metadata = self._extract_metadata(tree, script_type, script_id)
            
            # Validate script constraints
            self._validate_script(tree, metadata)
            
            # Create script instance
            return self._create_script(source, metadata)
            
        except SyntaxError as e:
            from script_engine.exceptions.parsing import ScriptParsingError
            raise ScriptParsingError(f"Invalid script syntax: {str(e)}")
            
    def _determine_script_type(self, tree: ast.AST) -> ScriptType:
        """Determine if the script is a strategy or indicator based on function definitions.

        A script is considered a strategy if it contains both setup() and process() functions.
        A script is considered an indicator if it assigns to an 'export' variable.

        Raises:
            ConflictingScriptTypeError: If script has both strategy and indicator characteristics
            MissingScriptTypeError: If script has neither strategy nor indicator characteristics
        """
        has_setup = False
        has_process = False
        has_export = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == "setup":
                    has_setup = True
                elif node.name == "process":
                    has_process = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "export":
                        has_export = True

        is_strategy = has_setup and has_process

        if is_strategy and has_export:
            from script_engine.exceptions.parsing_specific import ConflictingScriptTypeError
            raise ConflictingScriptTypeError(
                "Script cannot be both a strategy (has setup/process) and an indicator (has export)"
            )
        elif is_strategy:
            return ScriptType.STRATEGY
        elif has_export:
            return ScriptType.INDICATOR
        else:
            from script_engine.exceptions.parsing_specific import MissingScriptTypeError
            raise MissingScriptTypeError(
                "Script must be either a strategy (with setup/process functions) or an indicator (with export variable)"
            )
            
    def _extract_metadata(self, tree: ast.AST, script_type: ScriptType, script_id: str) -> ScriptMetadata:
        """Extract metadata from the script."""
        inputs = {}
        exports = set()
        # Dictionary to store custom imports: {alias: definition_id}
        custom_imports: Dict[str, str] = {}
        
        for node in ast.walk(tree):
            # Remove standard Python import handling, we use custom import_script
            # if isinstance(node, ast.Import):
            #     imports.extend(alias.name for alias in node.names)
            # elif isinstance(node, ast.ImportFrom):
            #     imports.append(node.module)
            if isinstance(node, ast.Call): # Changed from elif
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith("input."):
                        if node.args and isinstance(node.args[0], ast.Constant):
                            inputs[node.args[0].value] = None
            elif isinstance(node, ast.Assign):
                # Detect custom import assignments like: my_sma = import_script('indicators/sma.py')
                if isinstance(node.value, ast.Call) and \
                   isinstance(node.value.func, ast.Name) and \
                   node.value.func.id == 'import_script' and \
                   len(node.targets) == 1 and \
                   isinstance(node.targets[0], ast.Name) and \
                   len(node.value.args) == 1 and \
                   isinstance(node.value.args[0], ast.Constant) and \
                   isinstance(node.value.args[0].value, str):
                    
                    alias = node.targets[0].id
                    definition_id = node.value.args[0].value
                    if alias in custom_imports:
                         # Handle potential duplicate aliases if needed (e.g., raise error or log warning)
                         # Using logger requires importing logging
                         # logger.warning(f"Duplicate import alias '{alias}' detected. Overwriting previous import.")
                         pass # Or raise an error
                    custom_imports[alias] = definition_id
                # Detect export assignments
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("export"):
                        exports.add(target.id)

        return ScriptMetadata(
            id=script_id,
            name=script_id,
            type=script_type,
            inputs=inputs,
            exports=exports,
            imports=custom_imports # Use the correct variable name
        )
        
    def _validate_script(self, tree: ast.AST, metadata: ScriptMetadata) -> None:
        """Validate script against all constraints."""
        if metadata.type == ScriptType.STRATEGY:
            self._validate_strategy_script(tree)
        else:
            self._validate_indicator_script(tree)
            
    def _validate_strategy_script(self, tree: ast.AST) -> None:
        """Validate strategy script constraints."""
        # Check for required functions
        functions = {node.name for node in ast.walk(tree) 
                    if isinstance(node, ast.FunctionDef)}
        missing = self.required_strategy_functions - functions
        if missing:
            from script_engine.exceptions.parsing_specific import MissingRequiredFunctionsError
            raise MissingRequiredFunctionsError(f"Strategy script missing required functions: {missing}")
            
        # Check for input usage in process function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "process":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if isinstance(child.func.value, ast.Name) and child.func.value.id == "input":
                                from script_engine.exceptions.parsing_specific import InvalidInputUsageError
                                raise InvalidInputUsageError("Input functions cannot be used inside process()")

        # Warn about any variable assignments at module level (outside setup)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # Ignore ALL_CAPS constants only
                        if var_name.isupper():
                            continue
                        # Warn for all other assignments, including inputs
                        raise StrategyGlobalVariableError(f"Variable '{var_name}' assigned at global scope. Move all variable declarations inside setup() or process().")
                                
    def _validate_indicator_script(self, tree: ast.AST) -> None:
        """Validate indicator script constraints."""
        # Check for single export
        exports = {node.targets[0].id for node in ast.walk(tree)
                  if isinstance(node, ast.Assign)
                  and isinstance(node.targets[0], ast.Name)
                  and node.targets[0].id.startswith('export')}
        if len(exports) != 1:
            from script_engine.exceptions.parsing_specific import MultipleExportsError
            raise MultipleExportsError("Indicator script must have exactly one export")
            
        # Check for strategy function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"long", "short", "close", "position"}:
                        from script_engine.exceptions.parsing_specific import StrategyFunctionInIndicatorError
                        raise StrategyFunctionInIndicatorError("Indicator scripts cannot use strategy functions")
                        
    def _create_script(self, source: str, metadata: ScriptMetadata) -> Script:
        """Create script instance with source and metadata."""
        return Script(source, metadata)