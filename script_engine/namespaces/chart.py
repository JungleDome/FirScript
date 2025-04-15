from typing import Any, List, override

from ..namespaces.base import BaseNamespace

class ChartNamespace(BaseNamespace):
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

    def get_plots(self) -> List[dict]:
        """Get all registered plots for rendering."""
        return self._plots

    @override
    def generate_output(self) -> List[dict]:
        """Generate the final output for this namespace after script execution.

        Returns:
            A list of plot configurations for rendering.
        """
        return self.get_plots()