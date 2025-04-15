"""
Module for execution context classes used by the script engine runtime.
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ExecutionContext:
    """Holds the state and globals for a single script instance."""
    instance_id: str
    definition_id: str  # ID of the script definition (e.g., path)
    globals: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the execution context with safe builtins."""
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
