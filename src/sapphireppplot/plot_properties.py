"""Define PlotProperties class"""

from dataclasses import dataclass, field
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

    preview_size_1d : list[float]
        Preview window size in 1D.
    preview_size_2d : list[float]
        Preview window size in 2D.

    text_color : list[float]
        The text color for labels and legends.

    labels : dict[str, str]
        Labels for the series quantities in the chart.
    line_colors : dict[str, list[str]]
        Line colors for the series quantities in the LineChartView.
    line_styles : dict[str, str]
        Line styles for the series quantities in the LineChartView.

    grid_labels : list[str]
        Labels of the x,y and z axes for 2D/3D plots.

    color_map : str
        Select a color map for
    color_bar_position : str | list[float]
        Color bar postion.
        Either descriptive string or coordinates.
    color_bar_length : float
        Size of the color bar.
        Set to `0` to hide the color bar.
    """

    series_names: Optional[list[str]] = None
    data_type: str = "POINTS"

    preview_size_1d: list[float] = field(default_factory=lambda: [1280, 720])
    preview_size_2d: list[float] = field(default_factory=lambda: [1024, 1024])

    text_color: list[float] = field(default_factory=lambda: [0.5, 0.5, 0.5])

    labels: dict[str, str] = field(default_factory=dict)
    line_colors: dict[str, list[str]] = field(default_factory=dict)
    line_styles: dict[str, str] = field(default_factory=dict)

    grid_labels: list[str] = field(
        default_factory=lambda: [r"$x$", r"$y$", r"$z$"]
    )

    color_map: str = "Viridis (matplotlib)"
    color_bar_position: str | list[float] = field(
        # default_factory=lambda: [0.65, 0.1]
        default_factory=lambda: "Lower Right Corner"
    )
    color_bar_length: float = 0.25

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
            flat_dict = []
            for key, value in self.labels.items():
                flat_dict += [key, value]
            solution_display.SeriesLabel = flat_dict
        if self.line_colors:
            flat_dict = []
            for key, value in self.line_colors.items():
                flat_dict += [key, value[0], value[1], value[2]]
            solution_display.SeriesColor = flat_dict
        if self.line_styles:
            flat_dict = []
            for key, value in self.line_styles.items():
                flat_dict += [key, value]
            solution_display.SeriesLineStyle = flat_dict

    def show_data_grid(self, solution_display: paraview.servermanager.Proxy):
        """
        Set display properties to show the data_grid.

        Parameters
        ----------
        solution_display : paraview.servermanager.Proxy
            Solution display
        """
        solution_display.DataAxesGrid.GridAxesVisibility = 1
        solution_display.DataAxesGrid.XTitle = self.grid_labels[0]
        solution_display.DataAxesGrid.YTitle = self.grid_labels[1] + "  "
        # Only show Axes Min-X//Y/Z
        solution_display.DataAxesGrid.AxesToLabel = 7
        # solution_display.DataAxesGrid.FacesToRender = 7
        # Set default font size: 24 for title, 18 for label
        solution_display.DataAxesGrid.XTitleFontSize = 24
        solution_display.DataAxesGrid.YTitleFontSize = 24
        solution_display.DataAxesGrid.XLabelFontSize = 18
        solution_display.DataAxesGrid.YLabelFontSize = 18
        # Use gray color for label for good visibility in both light and dark mode
        solution_display.DataAxesGrid.XTitleColor = self.text_color
        solution_display.DataAxesGrid.YTitleColor = self.text_color
        solution_display.DataAxesGrid.XLabelColor = self.text_color
        solution_display.DataAxesGrid.YLabelColor = self.text_color
        solution_display.DataAxesGrid.GridColor = self.text_color

    def configure_color_bar(
        self, color_bar: paraview.servermanager.Proxy
    ) -> bool:
        """
        Configure the color bar.

        Parameters
        ----------
        color_bar : paraview.servermanager.Proxy
            Color bar.

        Returns
        -------
        bool
            `True` if color bar is visible, `False` otherwise.
        """
        color_bar.TitleFontSize = 24
        color_bar.LabelFontSize = 18
        color_bar.TitleColor = self.text_color
        color_bar.LabelColor = self.text_color

        if self.color_bar_length == 0:
            return False

        # change scalar bar placement
        match self.color_bar_position:
            case str():
                color_bar.WindowLocation = self.color_bar_position
            case _:
                color_bar.WindowLocation = "Any Location"
                color_bar.Position = self.color_bar_position
        color_bar.ScalarBarLength = self.color_bar_length

        return True
