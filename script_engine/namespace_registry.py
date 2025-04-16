import logging
from types import FunctionType
from typing import Any, Callable, Dict, Optional

from script_engine.namespaces.base import BaseNamespace
from script_engine.namespaces.chart import ChartNamespace
from script_engine.namespaces.color import ColorNamespace
from script_engine.namespaces.data import DataNamespace
from script_engine.namespaces.input import InputNamespace
from script_engine.namespaces.strategy import StrategyNamespace
from script_engine.namespaces.ta import TANamespace

logger = logging.getLogger(__name__)

class NamespaceRegistry:
    def __init__(self):
        self.namespaces: Dict[str, BaseNamespace] = {}
        self.shared: dict[str, Any] = {}

    def register(self, name: str, namespace: BaseNamespace | Callable) -> None:
        if not isinstance(namespace, BaseNamespace) and not callable(namespace):
            raise ValueError(f"Namespace '{name}' must be an instance of BaseNamespace")
        self.namespaces[name] = namespace
        
    def register_default_namespaces(self, inputs_override: Optional[Dict[str, Any]], column_mapping: Optional[Dict[str, str]] = None) -> None:
        """Initialize and register the default namespaces."""
        self.register("ta", TANamespace(self.shared))
        self.register("input", InputNamespace(self.shared, inputs_override or {}))
        self.register("chart", ChartNamespace(self.shared))
        self.register("color", ColorNamespace(self.shared))
        self.register("strategy", StrategyNamespace(self.shared))
        self.register("data", DataNamespace(self.shared, column_mapping))
        logger.debug("Default namespaces registered.")

    def get(self, name: str) -> BaseNamespace:
        return self.namespaces[name]

    def build(self) -> dict[str, BaseNamespace]:
        return self.namespaces.copy()

    @staticmethod
    def generate_outputs(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
        outputs = {}
        for name, namespace in namespaces.items():
            if not isinstance(namespace, BaseNamespace):
                continue
            output = namespace.generate_output()
            if output is not None:
                outputs[name] = output
        return outputs
    
    @staticmethod
    def generate_metadatas(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
        outputs = {}
        for name, namespace in namespaces.items():
            if not isinstance(namespace, BaseNamespace):
                continue
            output = namespace.generate_metadata()
            if output is not None:
                outputs[name] = output
        return outputs