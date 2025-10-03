"""Define PlotProperties class."""

from dataclasses import dataclass, field, replace
import copy
from typing import Optional, Any, Self
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
    camera_view_2d: tuple[bool, float] | Any
        The view for 2D render view.
        Can be any kind and number of arguments
        that will be passed to the `render_view.ResetCamera()` method.

    screenshot_transparent_background : bool
        Use a transparent background for screenshots?
        Defaults to `True`.
    animation_transparent_background : bool
        Use a transparent background for animations?
        Defaults to `False`.
        For animations it is recommended not to use a transparent background.
        Many formats like `.mp4` do not support it, resulting in artefacts.
        For `.gif` using a transparent background is possible.
    animation_frame_stride : int
        Frame stride for the animation snapshots.

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

    legend_location : str | list[float]
        Legend postion in LineChartView.
        Either descriptive string or coordinates.
    legend_symbol_width : int
        Size of the legend marker in LineChartView..
        Set to `0` to hide the legend.

    show_grid : bool
        Show the grid lines for 2D/3D plots.
    grid_labels : list[str]
        Labels of the x,y and z axes for 2D/3D plots.
    grid_color : list[float]
        The color of grid axes and legend for 2D/3D plots.

    color_map : str
        Select a color map for the color bar.
    color_bar_label_format : str
        The format string for the color bar labels,
        e.g. `r"%-#6.3g"`.
        Use automatic formatting if empty.
    color_bar_range_labels: bool
        Show range labels of the color bar?
    color_bar_range_label_format : str
        The format string for the color bar range labels,
        e.g. `r"%-#6.1e"`.
    color_bar_position : str | list[float]
        Color bar postion.
        Either descriptive string or coordinates.
    color_bar_length : float
        Size of the color bar.
        Set to `0` to hide the color bar.

    axes_scale : list[float]
        Divide the x,y,z-axes by this scale in the RenderView.
        This only affects the displayed axes ticks,
        it does not rescale the underlying data.
    axes_stretch : list[float]
        Stretch the x,y,z-axes by this factor in the RenderView.
        This does not change the displayed numbers,
        only makes the axes visually bigger/smaller.

    time_format : str
        Formatted text for the time.
    time_location : str | list[float]
        Text postion for time labeling.
        Either descriptive string or coordinates.

    sampling_pattern : str
        Sampling pattern used for plot_over_line.
    sampling_resolution : int | float, optional
        Sampling resolution used for plot_over_line.
        Number of points for uniform sampling,
        `Tolerance` for center and boundary.

    stream_tracer_maximum_error : float
        Maximum error for stream_tracer.
    stream_tracer_minimum_step : float
        Minimum step length for stream_tracer.
    stream_tracer_initial_step : float
        Initial step length for stream_tracer.
    stream_tracer_maximum_step : float
        Maximum step length for stream_tracer.
    """

    series_names: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    data_type: str = "POINTS"

    preview_size_1d: list[float] = field(default_factory=lambda: [1280, 720])
    preview_size_2d: list[float] = field(default_factory=lambda: [1024, 1024])
    camera_view_2d: tuple[bool, float] | Any = field(
        default_factory=lambda: (False, 0.9)
    )

    screenshot_transparent_background: bool = True
    animation_transparent_background: bool = False
    animation_frame_stride: int = 1

    text_color: list[float] = field(default_factory=lambda: [0.5, 0.5, 0.5])
    label_size: int = 18
    text_size: int = 24
    title_size = 30

    line_colors: dict[str, list[str]] = field(default_factory=dict)
    line_styles: dict[str, str] = field(default_factory=dict)

    legend_location: str | list[float] = field(
        default_factory=lambda: "TopRight"
    )
    legend_symbol_width: int = 30

    show_grid: bool = False
    grid_labels: list[str] = field(
        default_factory=lambda: [r"$x$", r"$y$", r"$z$"]
    )
    grid_color: list[float] = field(default_factory=lambda: [0.5, 0.5, 0.5])

    color_map: str = "Viridis (matplotlib)"
    color_bar_label_format: str = ""
    color_bar_range_labels: bool = True
    color_bar_range_label_format: str = r"%-#6.1e"
    color_bar_position: str | list[float] = field(
        # default_factory=lambda: [0.65, 0.1]
        default_factory=lambda: "Lower Right Corner"
    )
    color_bar_length: float = 0.25

    axes_scale: list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    axes_stretch: list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])

    time_format: str = r"Time: {time:.2f}"
    time_location: str | list[float] = "Upper Left Corner"

    sampling_pattern: str = "center"
    sampling_resolution: Optional[int | float] = None

    stream_tracer_maximum_error: float = 1e-6
    stream_tracer_minimum_step: float = 0.01
    stream_tracer_initial_step: float = 0.2
    stream_tracer_maximum_step: float = 0.5

    def copy(self) -> Self:
        """
        Create a deep copy of the PlotProperties.

        Returns
        -------
        PlotProperties
            Copy of the PlotProperties.
        """
        return copy.deepcopy(self)

    def replace(self, **kwargs: Any) -> Self:
        """
        Copy and replace variables in the PlotProperties.

        Returns
        -------
        PlotProperties
            Copy of the PlotProperties with replaced values.
        """
        return replace(self, **kwargs)

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
        match self.legend_location:
            case str():
                line_chart_view.LegendLocation = self.legend_location
            case list():
                line_chart_view.LegendLocation = "Custom"
                line_chart_view.LegendPosition = self.legend_location
            case _:
                raise TypeError(
                    f"Unsupported `legend_location` type "
                    f"{type(self.legend_location)}: {self.legend_location}"
                )
        if self.legend_symbol_width == 0:
            line_chart_view.ShowLegend = False
        else:
            line_chart_view.ShowLegend = True
            line_chart_view.LegendSymbolWidth = self.legend_symbol_width

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

    def configure_grid_2d(
        self,
        render_view: paraview.servermanager.Proxy,
        solution_display: paraview.servermanager.Proxy,
    ) -> None:
        """
        Configure display properties to show the grid in 2d.

        Parameters
        ----------
        render_view : paraview.servermanager.Proxy
            Render view.
        solution_display : paraview.servermanager.Proxy
            Solution display.
        """
        if self.show_grid:
            solution_display.SetRepresentationType("Surface With Edges")
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
        render_view.AxesGrid.XTitleColor = self.grid_color
        render_view.AxesGrid.YTitleColor = self.grid_color
        render_view.AxesGrid.XLabelColor = self.grid_color
        render_view.AxesGrid.YLabelColor = self.grid_color
        render_view.AxesGrid.GridColor = self.grid_color
        # scale axes
        solution_display.Scale = self.axes_stretch
        render_view.AxesGrid.DataScale = [
            self.axes_stretch[0] * self.axes_scale[0],
            self.axes_stretch[1] * self.axes_scale[1],
            self.axes_stretch[2] * self.axes_scale[2],
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
        if self.color_bar_label_format:
            color_bar.AutomaticLabelFormat = False
            color_bar.LabelFormat = self.color_bar_label_format
        color_bar.AddRangeLabels = self.color_bar_range_labels
        color_bar.RangeLabelFormat = self.color_bar_range_label_format

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
