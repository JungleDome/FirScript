"""
Module for execution input classes used by the script engine runtime.
"""
import copy
import pandas as pd
from typing import Optional


class ExecutionInputBase:
    """Base class for data provided to the script execution context."""
    def __init__(self,
                 current: Optional[pd.Series] = None,
                 all: Optional[pd.DataFrame] = None,
                 raw_all: Optional[pd.DataFrame] = None):
        """
        Initialize the execution input.
        
        Args:
            current: The current data point (typically a Series)
            all: All data points processed through column mapping
            raw_all: All raw data points without column mapping
        """
        self.current = current
        self.all = all
        self.raw_all = raw_all

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
