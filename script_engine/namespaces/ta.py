from typing import Any
import pandas as pd

class TANamespace:
    """Technical Analysis namespace implementation."""
    
    @staticmethod
    def ema(series: pd.Series, length: int) -> float:
        """Calculate Exponential Moving Average."""
        return series.ewm(span=length).mean().iloc[-1]

    @staticmethod 
    def rsi(series: pd.Series, length: int) -> float:
        """Calculate Relative Strength Index."""
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=length).mean()
        avg_loss = loss.rolling(window=length).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs.iloc[-1]))