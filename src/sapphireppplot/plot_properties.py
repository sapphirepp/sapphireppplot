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
    data_type : str
        Specifies if solution has DG (`POINTS`) or VE (`CELLS`) data.
    labels : Optional[list[str]]
        Labels for the series quantities in the chart.
    line_colors : Optional[list[str]]
        Line colors for the series quantities in the LineChartView.
    line_styles : Optional[list[str]]
        Line styles for the series quantities in the LineChartView.
    color_map : str
        Select a color map for
    """

    series_names: Optional[list[str]] = None
    data_type: str = "POINTS"
    labels: Optional[list[str]] = None
    line_colors: Optional[list[str]] = None
    line_styles: Optional[list[str]] = None
    color_map: str = "Viridis (matplotlib)"

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

    def show_data_grid(self, solution_display: paraview.servermanager.Proxy):
        """
        Set display properties to show the data_grid.

        Parameters
        ----------
        solution_display : paraview.servermanager.Proxy
            Solution display
        """
        solution_display.DataAxesGrid.GridAxesVisibility = 1
        solution_display.DataAxesGrid.XTitle = "$x$"
        solution_display.DataAxesGrid.YTitle = "$y$  "
        # Only show Axes Min-X//Y/Z
        solution_display.DataAxesGrid.AxesToLabel = 7
        # solution_display.DataAxesGrid.FacesToRender = 7
        # Set default font size: 24 for title, 18 for label
        solution_display.DataAxesGrid.XTitleFontSize = 24
        solution_display.DataAxesGrid.YTitleFontSize = 24
        solution_display.DataAxesGrid.XLabelFontSize = 18
        solution_display.DataAxesGrid.YLabelFontSize = 18
        # Use gray color for label for good visibility in both light and dark mode
        solution_display.DataAxesGrid.XTitleColor = [0.5, 0.5, 0.5]
        solution_display.DataAxesGrid.YTitleColor = [0.5, 0.5, 0.5]
        solution_display.DataAxesGrid.XLabelColor = [0.5, 0.5, 0.5]
        solution_display.DataAxesGrid.YLabelColor = [0.5, 0.5, 0.5]
        solution_display.DataAxesGrid.GridColor = [0.5, 0.5, 0.5]
