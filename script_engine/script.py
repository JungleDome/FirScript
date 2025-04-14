# Proposed rewrite for script_engine/script.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Set, Optional
import uuid

class ScriptType(Enum):
    STRATEGY = "strategy"
    INDICATOR = "indicator"

@dataclass
class ScriptMetadata:
    """Stores metadata parsed from the script source."""
    id: str  # Usually the name/path provided during import/load
    name: str # Optional descriptive name from script (e.g., study(name="..."))
    type: ScriptType
    inputs: Dict[str, Any] = field(default_factory=dict)
    exports: Set[str] = field(default_factory=set) # Variables intended for export
    imports: Dict[str, str] = field(default_factory=dict) # Alias -> script_id mapping

@dataclass
class Script:
    """Represents a parsed script ready for execution."""
    source: str
    metadata: ScriptMetadata
    # Unique identifier for this specific script definition (e.g., file path or hash)
    # Used to retrieve the source code.
    definition_id: str = field(init=False)

    def __post_init__(self):
        # Use metadata.id as the primary identifier for the script definition
        self.definition_id = self.metadata.id

    @property
    def id(self) -> str:
        """Returns the primary identifier (e.g., path/name) of the script."""
        return self.metadata.id

    @property
    def name(self) -> str:
        """Returns the descriptive name from the script metadata."""
        return self.metadata.name

    @property
    def type(self) -> ScriptType:
        """Returns the type of the script (Strategy or Indicator)."""
        return self.metadata.type