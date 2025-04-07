from typing import Any

class StrategyNamespace:
    """Handles strategy order management and position tracking."""
    
    def __init__(self):
        self._orders = []
        self._position = None

    def long(self, **kwargs) -> None:
        """Enter a long position."""
        self._orders.append({
            'type': 'long',
            'options': kwargs
        })

    def short(self, **kwargs) -> None:
        """Enter a short position."""
        self._orders.append({
            'type': 'short', 
            'options': kwargs
        })

    def close(self, **kwargs) -> None:
        """Close current position."""
        self._orders.append({
            'type': 'close',
            'options': kwargs
        })

    def position(self) -> dict:
        """Get current position info."""
        return self._position or {
            'size': 0,
            'entry_price': 0,
            'profit': 0
        }