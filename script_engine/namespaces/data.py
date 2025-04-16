from typing import Any
import pandas as pd
from script_engine.namespaces.base import BaseNamespace

class DataNamespace(BaseNamespace):
    key = 'data'
    
    def __init__(self, shared: dict[str, Any], column_mapping: dict[str, str] = None):
        super().__init__(shared)
        
        self.column_mapping = column_mapping
        self.__raw_all: pd.DataFrame = None
        self.__all: pd.DataFrame = None
        self.__current_bar: pd.Series = None

    def set_current_bar(self, bar: pd.Series):
        self.__current_bar = bar
        self.shared.setdefault(self.key, {})['current'] = bar
        
    def set_all_bar(self, bars: pd.DataFrame):
        self.__raw_all = bars
        self.shared.setdefault(self.key, {})['raw_all'] = self.__raw_all
        self.__all = self.rename_columns(bars)
        self.shared.setdefault(self.key, {})['all'] = self.__all

    def rename_columns(self, df: pd.DataFrame):
        if not self.column_mapping:
            return df
        return df.rename(columns=self.column_mapping)

    @property
    def current(self):
        return self.__current_bar

    @property
    def all(self):
        return self.__all
    
    @property
    def raw_all(self):
        return self.__raw_all