from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

class ScriptType(Enum):
    STRATEGY = "strategy"
    INDICATOR = "indicator"

@dataclass
class ScriptMetadata:
    name: str
    type: ScriptType
    inputs: Dict[str, Any]
    exports: Set[str]
    imports: List[str]

class Script(ABC):
    def __init__(self, source: str):
        self.source = source
        self.metadata: Optional[ScriptMetadata] = None
        
    @abstractmethod
    def validate(self) -> bool:
        """Validate the script against all constraints."""
        pass
    
    @abstractmethod
    def extract_metadata(self) -> ScriptMetadata:
        """Extract metadata about the script (type, inputs, exports, imports)."""
        pass
    
    def setup(self, **kwargs) -> None:
        """Optional setup method for strategy scripts."""
        pass
    
    def process(self, bar: Any) -> None:
        """Optional process method for strategy scripts."""
        pass
    
    @property
    def export(self) -> Any:
        """Export value for indicator scripts."""
        raise NotImplementedError("Indicator scripts must implement export property") 