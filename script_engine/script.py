from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple

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
    custom_imports: List[Tuple[str, str]]

class Script:
    id: str
    
    def __init__(self, source: str, metadata: ScriptMetadata):
        self.source = source
        self.metadata = metadata
        self.id = metadata.name or hash(source)