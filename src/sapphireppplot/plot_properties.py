"""Define PlotProperties class."""

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
    labels : dict[str, str]
        Labels for the series quantities in the chart.
    data_type : str
        Specifies if solution has DG (`POINTS`) or VE (`CELLS`) data.

    preview_size_1d : list[float]
        Preview window size in 1D.
    preview_size_2d : list[float]
        Preview window size in 2D.

    text_color : list[float]
        The text color for labels and legends.
    label_size : int
        Font size for label text.
    text_size : int
        Font size for text, e.g. legend and axes titles.
    title_size : int
        Font size for chart titles.

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

    scale_x : float
        Scaling factor for x-axes.
    scale_y : float
        Scaling factor for y-axes.
    scale_z : float
        Scaling factor for z-axes.

    sampling_pattern : str
        Sampling pattern used for plot_over_line.
    sampling_resolution : int | float, optional
        Sampling resolution used for plot_over_line.
        Number of points for uniform sampling,
        `Tolerance` for center and boundary.
    """

    series_names: Optional[list[str]] = None
    labels: dict[str, str] = field(default_factory=dict)
    data_type: str = "POINTS"

    preview_size_1d: list[float] = field(default_factory=lambda: [1280, 720])
    preview_size_2d: list[float] = field(default_factory=lambda: [1024, 1024])

    text_color: list[float] = field(default_factory=lambda: [0.5, 0.5, 0.5])
    label_size: int = 18
    text_size: int = 24
    title_size = 30

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

    scale_x: float = 1.0
    scale_y: float = 1.0
    scale_z: float = 1.0

    sampling_pattern: str = "center"
    sampling_resolution: Optional[int | float] = None

    def configure_line_chart_view_axes(
        self, line_chart_view: paraview.servermanager.Proxy
    ) -> None:
        """
        Configure axes of a LineChartView.

        Parameters
        ----------
        line_chart_view : paraview.servermanager.Proxy
            ParaView LineChartView object.
        """
        line_chart_view.ChartTitleFontSize = self.title_size
        line_chart_view.LeftAxisTitleFontSize = self.text_size
        line_chart_view.BottomAxisTitleFontSize = self.text_size
        line_chart_view.LegendFontSize = self.label_size
        line_chart_view.LeftAxisLabelFontSize = self.label_size
        line_chart_view.BottomAxisLabelFontSize = self.label_size

    def configure_line_chart_view_display(
        self, solution_display: paraview.servermanager.Proxy
    ) -> None:
        """
        Configure display properties for a LineChartView.

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

    def show_grid_2d(
        self,
        render_view: paraview.servermanager.Proxy,
        solution_display: paraview.servermanager.Proxy,
    ) -> None:
        """
        Set display properties to show the grid in 2d.

        Parameters
        ----------
        render_view : paraview.servermanager.Proxy
            Render view.
        solution_display : paraview.servermanager.Proxy
            Solution display.
        """
        render_view.AxesGrid.Visibility = 1
        render_view.AxesGrid.XTitle = self.grid_labels[0]
        render_view.AxesGrid.YTitle = self.grid_labels[1] + "  "
        # Only show Axes Min-X//Y/Z
        render_view.AxesGrid.AxesToLabel = 7
        # render_view.AxesGrid.FacesToRender = 7
        # Set default font size
        render_view.AxesGrid.XTitleFontSize = self.text_size
        render_view.AxesGrid.YTitleFontSize = self.text_size
        render_view.AxesGrid.XLabelFontSize = self.label_size
        render_view.AxesGrid.YLabelFontSize = self.label_size
        # Use gray color for label for good visibility in both light and dark mode
        render_view.AxesGrid.XTitleColor = self.text_color
        render_view.AxesGrid.YTitleColor = self.text_color
        render_view.AxesGrid.XLabelColor = self.text_color
        render_view.AxesGrid.YLabelColor = self.text_color
        render_view.AxesGrid.GridColor = self.text_color
        # scale axes
        solution_display.Scale = [self.scale_x, self.scale_y, self.scale_z]
        render_view.AxesGrid.DataScale = [
            self.scale_x,
            self.scale_y,
            self.scale_z,
        ]

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
        color_bar.TitleFontSize = self.text_size
        color_bar.LabelFontSize = self.label_size
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
