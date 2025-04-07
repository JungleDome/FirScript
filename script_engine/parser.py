import ast
from typing import List, Set, Tuple
from .script import Script, ScriptType, ScriptMetadata
from typing import Tuple

class ScriptParser:
    def __init__(self):
        self.required_strategy_functions = {"setup", "process"}
        self.allowed_namespaces = {"ta", "input", "chart", "color", "strategy"}
        
    def parse(self, source: str) -> Script:
        """Parse and validate a script source."""
        try:
            tree = ast.parse(source)
            script_type = self._determine_script_type(tree)
            
            # Extract metadata
            metadata = self._extract_metadata(tree, script_type)
            
            # Validate script constraints
            self._validate_script(tree, metadata)
            
            # Create appropriate script instance
            script = self._create_script(source, metadata)
            script.metadata = metadata
            return script
            
        except SyntaxError as e:
            raise ValueError(f"Invalid script syntax: {str(e)}")
            
    def _determine_script_type(self, tree: ast.AST) -> ScriptType:
        """Determine if the script is a strategy or indicator."""
        has_strategy_calls = False
        has_export = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"long", "short", "close", "position"}:
                        has_strategy_calls = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "export":
                        has_export = True
                        
        if has_strategy_calls and has_export:
            raise ValueError("Script cannot be both a strategy and an indicator")
        elif has_strategy_calls:
            return ScriptType.STRATEGY
        elif has_export:
            return ScriptType.INDICATOR
        else:
            raise ValueError("Script must be either a strategy or an indicator")
            
    def _extract_metadata(self, tree: ast.AST, script_type: ScriptType) -> ScriptMetadata:
        """Extract metadata from the script."""
        inputs = {}
        custom_imports = []  # Initialize custom_imports list
        exports = set()
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith("input."):
                        # Extract input parameters
                        if node.args and isinstance(node.args[0], ast.Constant):
                            inputs[node.args[0].value] = None
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "import":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name) and node.value.func.id == "import":
                                import_path = node.value.args[0].s
                                custom_imports.append(("indicator", import_path))
                        
        return ScriptMetadata(
            custom_imports=custom_imports,  # Add custom imports to metadata
            name="",  # Will be set by the script instance
            type=script_type,
            inputs=inputs,
            exports=exports,
            imports=imports
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
            raise ValueError(f"Strategy script missing required functions: {missing}")
            
        # Check for input usage in process function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "process":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr.startswith("input."):
                                raise ValueError("Input functions cannot be used inside process()")
                                
    def _validate_indicator_script(self, tree: ast.AST) -> None:
        """Validate indicator script constraints."""
        # Check for single export
        exports = {node.targets[0].id for node in ast.walk(tree)
                  if isinstance(node, ast.Assign)
                  and isinstance(node.targets[0], ast.Name)}
        if len(exports) != 1:
            raise ValueError("Indicator script must have exactly one export")
            
        # Check for strategy function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"long", "short", "close", "position"}:
                        raise ValueError("Indicator scripts cannot use strategy functions")
                        
    def _create_script(self, source: str, metadata: ScriptMetadata) -> Script:
        """Create appropriate script instance based on type."""
        # This is a placeholder - actual implementation will create proper script instances
        return Script(source) 