"""Define PlotProperties class"""

from dataclasses import dataclass
from typing import Optional
import paraview.servermanager


@dataclass
class PlotProperties:
    """
    Class to collect properties for plotting.

    Attributes
    ----------
    series_names : Optional[list[str]]
        Names of the series to load and show.
    labels : Optional[list[str]]
        Labels for the series quantities in the chart.
    line_colors : Optional[list[str]]
        Line colors for the series quantities in the LineChartView.
    line_styles : Optional[list[str]]
        Line styles for the series quantities in the LineChartView.
    """

    series_names: Optional[list[str]] = None
    labels: Optional[list[str]] = None
    line_colors: Optional[list[str]] = None
    line_styles: Optional[list[str]] = None

    def set_display_properties_line_chart_view(
        self, solution_display: paraview.servermanager.Proxy
    ):
        """
        Set display properties for a LineChartView.

        Parameters
        ----------
        solution_display : paraview.servermanager.Proxy
            Solution display
        """
        if self.labels:
            solution_display.SeriesLabel = self.labels
        if self.line_colors:
            solution_display.SeriesColor = self.line_colors
        if self.line_styles:
            solution_display.SeriesLineStyle = self.line_styles
