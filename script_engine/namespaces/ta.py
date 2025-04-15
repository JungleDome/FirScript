from typing import Any
import pandas as pd
import talipp.indicators as ta
from ..namespaces.base import BaseNamespace


class TANamespace(BaseNamespace):
    """Technical Analysis namespace implementation."""

    @staticmethod
    def sma(series: pd.Series, length: int) -> float:
        """Calculate Simple Moving Average."""
        return ta.SMA(period=length, input_values=series.to_list())

    @staticmethod
    def ema(series: pd.Series, length: int) -> float:
        """Calculate Exponential Moving Average."""
        return ta.EMA(period=length, input_values=series.to_list())

    @staticmethod
    def rsi(series: pd.Series, length: int) -> float:
        """Calculate Relative Strength Index."""
        return ta.RSI(period=length, input_values=series.to_list())

    @staticmethod
    def atr(df: pd.DataFrame, length: int) -> float:
        """Calculate Average True Range."""

        ohlcv_list = [
            ta.OHLCV(open=o, high=h, low=l, close=c, volume=v)
            for o, h, l, c, v in zip(
                df["open"], df["high"], df["low"], df["close"], df["volume"]
            )
        ]

        return ta.ATR(
            period=length,
            input_values=ohlcv_list
        )
