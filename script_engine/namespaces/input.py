from typing import Any, Dict

class InputNamespace:
    """Handles script input parameters."""
    
    def __init__(self, inputs: Dict[str, Any]):
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