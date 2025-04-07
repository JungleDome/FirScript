from typing import Any

class ChartNamespace:
    """Handles chart drawing and plotting operations."""
    
    def __init__(self):
        self._plots = []

    def plot(self, series: Any, **kwargs) -> None:
        """Plot a series on the chart."""
        self._plots.append({
            'data': series,
            'options': kwargs
        })

    def line(self, price: float, **kwargs) -> None:
        """Draw a horizontal line on the chart."""
        self._plots.append({
            'type': 'line',
            'price': price,
            'options': kwargs
        })

    def get_plots(self) -> list:
        """Get all registered plots for rendering."""
        return self._plots