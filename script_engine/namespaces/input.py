from typing import Any, Dict
from ..namespaces.base import BaseNamespace

class InputNamespace(BaseNamespace):
    """Handles script input parameters."""
    key = 'input'
    
    def __init__(self, shared: dict[str, Any], inputs: Dict[str, Any]):
        super().__init__(shared)
        
        self._inputs = inputs

    def int(self, name: str, default: int, **kwargs) -> int:
        """Get integer input parameter."""
        return int(self._inputs.get(name, default))

    def float(self, name: str, default: float, **kwargs) -> float:
        """Get float input parameter."""
        return float(self._inputs.get(name, default))

    def text(self, name: str, default: str, **kwargs) -> str:
        """Get text input parameter."""
        return self._inputs.get(name, default)

    def bool(self, name: str, default: bool, **kwargs) -> bool:
        """Get boolean input parameter."""
        return bool(self._inputs.get(name, default))