"""Define PlotProperties class."""

from dataclasses import dataclass, field, replace
import copy
from typing import Optional, Any, Self, Literal
from matplotlib.typing import ColorType
import matplotlib.colors
import paraview.servermanager


@dataclass
class PlotProperties:
    """
    Class to collect properties for plotting.
    """

    series_names: list[str] = field(default_factory=list)
    """Optional list of the series names to load and show."""
    labels: dict[str, str] = field(default_factory=dict)
    """Labels for the series quantities in the chart."""
    data_type: Literal["POINTS", "CELLS", "ROWS"] = "POINTS"
    """Specifies if solution has DG ("POINTS") or FV ("CELLS") data."""
    representation_type: (
        Literal[
            "UnstructuredGridRepresentation",
            "UniformGridRepresentation",
            "StructuredGridRepresentation",
            "GeometryRepresentation",
        ]
        | str
    ) = "UnstructuredGridRepresentation"
    """Specifies ParaView representation type for RenderView."""
    use_legacy_pvtu_reader: bool = True
    """
    For deal.II versions < 9.8.0 there was a bug that ``pvtu`` files had no time information.
    The legacy pvtu-reader addresses this problem by time-shifting the solution.
    If a newer version of deal.II >= 9.8.0 is used,
    this is not needed and one can set ``use_legacy_pvtu_reader=False``.

    Warning
    -------
    The default value for this variable is ``True`` for backwards compatibility.
    This default will change to ``False`` in a future version.
    """

    preview_size_1d: tuple[int, int] = field(
        default_factory=lambda: (1280, 720)
    )
    """
    Preview window size in 1D.
    Use ``preview_size = (0, 0)`` to deactivate preview mode.
    """
    preview_size_2d: tuple[int, int] = field(
        default_factory=lambda: (1024, 1024)
    )
    """Preview window size in 2D."""
    camera_view_2d: tuple[bool, float] | Any = field(
        default_factory=lambda: (False, 0.9)
    )
    """
    The view for 2D render view.
    Can be any kind and number of arguments
    that will be passed to the ``render_view.ResetCamera()`` method.

    See Also
    --------
    :pv:`paraview.simple.ResetCamera <paraview.simple.html#paraview.simple.ResetCamera>` :
        ParaView method to reset camera view.
    """
    preview_size_3d: tuple[int, int] = field(
        default_factory=lambda: (1024, 1024)
    )
    """Preview window size in 3D."""
    camera_view_3d: tuple[bool, float] | Any = field(
        default_factory=lambda: (False, 0.9)
    )
    """
    The view for 3D render view.
    Can be any kind and number of arguments
    that will be passed to the ``render_view.ResetCamera()`` method.

    See Also
    --------
    :pv:`paraview.simple.ResetCamera <paraview.simple.html#paraview.simple.ResetCamera>` :
        ParaView method to reset camera view.
    """

    screenshot_transparent_background: bool = True
    """Use a transparent background for screenshots?"""
    animation_transparent_background: bool = False
    """
    Use a transparent background for animations?
    Defaults to ``False``.
    For animations it is recommended not to use a transparent background.
    Many formats like ``.mp4`` do not support it, resulting in artefacts.
    For ``.gif`` using a transparent background is possible.
    """
    animation_frame_stride: int = 1
    """
    Frame stride for the animation snapshots.
    Use ``animation_frame_stride = -1`` to disable animations.
    """

    extracts_frame_stride: int = 1
    """Frame stride for the saving extracts."""
    extracts_compressor: Literal["None", "LZ4", "ZLib", "LZMA"] = "ZLib"
    """Compressor type for extracts."""
    extracts_compression_level: int = 5
    """
    Compression level for extracts.

    A value between 1 (fastest write) to 9 (smallest filesize).
    """

    font_family: Literal["Arial", "Courier", "Times"] = "Arial"
    """The font family for labels and legends."""
    text_color: ColorType = field(default_factory=lambda: (0.5, 0.5, 0.5))
    """The text color for labels and legends."""
    label_size: int = 18
    """Font size for label text."""
    text_size: int = 24
    """Font size for text, e.g. legend and axes titles."""
    title_size: int = 30
    """Font size for chart titles."""

    line_colors: dict[str, ColorType] = field(default_factory=dict)
    """Line colors for the series quantities in the LineChartView."""
    line_styles: dict[str, str] = field(default_factory=dict)
    """
    Line styles for the series quantities in the LineChartView.

    - "0" for None (default)
    - "1" for Solid
    - "2" for Dash
    - "3" for Dot
    - "4" for Dash Dot
    - "5" for Dash Dot Dot

    If no line style is set for a quantity,
    it default to None,
    making the line invisible.
    """
    line_widths: dict[str, float] = field(default_factory=dict)
    """Line widths or thickness for the series quantities in the LineChartView."""
    default_line_width: float = 2.0
    """Default line width or thickness in the LineChartView."""

    legend_location: (
        Literal[
            "TopLeft",
            "Top",
            "TopRight",
            "Left",
            "Right",
            "BottomLeft",
            "Bottom",
            "BottomRight",
        ]
        | tuple[float, float]
    ) = "TopRight"
    """
    Legend postion in LineChartView.
    Either descriptive string or coordinates.
    """
    legend_symbol_width: int = 30
    """
    Size of the legend marker in LineChartView.
    Set to ``0`` to hide the legend.
    """

    left_axis_labels: dict[float, str] = field(default_factory=dict)
    """Custom axis labels for left axes in LineChartView."""
    bottom_axis_labels: dict[float, str] = field(default_factory=dict)
    """Custom axis labels for bottom axes in LineChartView."""

    show_grid: bool = False
    """Show the grid lines for 2D/3D plots?"""
    grid_labels: tuple[str, str, str] = field(
        default_factory=lambda: (r"$x$", r"$y$", r"$z$")
    )
    """Labels of the x,y and z axes for 2D/3D plots."""
    grid_color: ColorType = field(default_factory=lambda: (0.5, 0.5, 0.5))
    """The color of grid axes and legend for 2D/3D plots."""

    color_map: str = "Viridis (matplotlib)"
    """Select a color map for the color bar."""
    color_bar_label_format: str = ""
    """
    The format string for the color bar labels,
    e.g. ``r"%-#6.3g"``.
    Use automatic formatting if empty.
    """
    color_bar_range_labels: bool = True
    """Show range labels of the color bar?"""
    color_bar_range_label_format: str = r"%-#6.1e"
    """
    The format string for the color bar range labels,
    e.g. ``r"%-#6.1e"``.
    """
    color_bar_orientation: Literal["Vertical", "Horizontal"] = "Vertical"
    """Orientation of the color bar."""
    color_bar_position: (
        Literal[
            "Upper Left Corner",
            "Upper Center",
            "Upper Right Corner",
            "Lower Left Corner",
            "Lower Center",
            "Lower Right Corner",
        ]
        | tuple[float, float]
    ) = "Lower Right Corner"
    """
    Color bar postion.
    Either descriptive string or coordinates.
    """
    color_bar_length: float = 0.25
    """
    Size of the color bar.
    Set to ``0`` to hide the color bar.
    """
    color_bar_thickness: int = 16
    """Thickness of the color bar."""

    axes_scale: tuple[float, float, float] = field(
        default_factory=lambda: (1.0, 1.0, 1.0)
    )
    """
    Divide the x,y,z-axes by this scale in the RenderView.
    This only affects the displayed axes ticks,
    it does not rescale the underlying data.
    """
    axes_stretch: tuple[float, float, float] = field(
        default_factory=lambda: (1.0, 1.0, 1.0)
    )
    """
    Stretch the x,y,z-axes by this factor in the RenderView.
    This does not change the displayed numbers,
    only makes the axes visually bigger/smaller.
    """
    axes_ticks: tuple[
        Optional[list[float]], Optional[list[float]], Optional[list[float]]
    ] = field(default_factory=lambda: (None, None, None))
    """
    Custom axes ticks for x,y,z-axes in RenderView.
    """

    time_format: str = r"$t = {time:.2f}$"
    """Formatted text for the time."""
    time_location: (
        Literal[
            "Upper Left Corner",
            "Upper Center",
            "Upper Right Corner",
            "Lower Left Corner",
            "Lower Center",
            "Lower Right Corner",
        ]
        | tuple[float, float]
    ) = "Upper Left Corner"
    """
    Text postion for time labeling.
    Either descriptive string or coordinates.
    """

    sampling_pattern: Literal["uniform", "center", "boundary"] = "center"
    """
    Sampling pattern used for plot_over_line.

    - "uniform" for ``Sample Uniformly``
    - "center" for ``Sample At Segment Centers``
    - "boundary" for ``Sample At Cell Boundaries``
    """
    sampling_resolution: Optional[int | float] = None
    """
    Sampling resolution used for plot_over_line.
    Number of points for "uniform" sampling,
    ``Tolerance`` for "center" and "boundary".

    See Also
    --------
    sapphireppplot.transform.plot_over_line
    """

    stream_tracer_maximum_error: float = 1e-6
    """Maximum error for stream_tracer."""
    stream_tracer_minimum_step: float = 0.01
    """Minimum step length for stream_tracer."""
    stream_tracer_initial_step: float = 0.2
    """Initial step length for stream_tracer."""
    stream_tracer_maximum_step: float = 0.5
    """
    Maximum step length for stream_tracer.

    See Also
    --------
    sapphireppplot.transform.stream_tracer
    """

    export_precision: int = 5
    """Precision for exporting data, e.g. as CSV"""

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
        line_chart_view
            ParaView LineChartView object.
        """
        # Set font family
        line_chart_view.ChartTitleFontFamily = self.font_family
        line_chart_view.LeftAxisTitleFontFamily = self.font_family
        line_chart_view.BottomAxisTitleFontFamily = self.font_family
        line_chart_view.LegendFontFamily = self.font_family
        line_chart_view.LeftAxisLabelFontFamily = self.font_family
        line_chart_view.BottomAxisLabelFontFamily = self.font_family
        # Set default font size
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
            case tuple():
                line_chart_view.LegendLocation = "Custom"
                line_chart_view.LegendPosition = list(self.legend_location)
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
        if self.left_axis_labels:
            flat_dict = []
            for key, label in self.left_axis_labels.items():
                flat_dict += [str(key), str(label)]
            line_chart_view.LeftAxisUseCustomLabels = 1
            line_chart_view.LeftAxisLabels = flat_dict
        if self.bottom_axis_labels:
            flat_dict = []
            for key, label in self.bottom_axis_labels.items():
                flat_dict += [str(key), str(label)]
            line_chart_view.BottomAxisUseCustomLabels = 1
            line_chart_view.BottomAxisLabels = flat_dict

    def configure_line_chart_view_display(
        self, solution_display: paraview.servermanager.Proxy
    ) -> None:
        """
        Configure display properties for a LineChartView.

        Parameters
        ----------
        solution_display
            Solution display
        """
        if self.labels:
            flat_dict = []
            for key in self.series_names:
                label = self.labels.get(key, key)
                flat_dict += [key, label]
            solution_display.SeriesLabel = flat_dict
        if self.line_colors:
            flat_dict = []
            default_color = "black"
            for key in self.series_names:
                color = self.line_colors.get(key, default_color)
                flat_dict += [
                    key,
                    str(matplotlib.colors.to_rgb(color)[0]),
                    str(matplotlib.colors.to_rgb(color)[1]),
                    str(matplotlib.colors.to_rgb(color)[2]),
                ]
            solution_display.SeriesColor = flat_dict
        if self.line_styles:
            flat_dict = []
            default_style = "1"
            for key in self.series_names:
                line_style = self.line_styles.get(key, default_style)
                flat_dict += [key, line_style]
            solution_display.SeriesLineStyle = flat_dict
        if self.line_widths:
            flat_dict = []
            for key in self.series_names:
                line_width = self.line_widths.get(key, self.default_line_width)
                flat_dict += [key, str(line_width)]
            solution_display.SeriesLineThickness = flat_dict

    def configure_grid_2d(
        self,
        render_view: paraview.servermanager.Proxy,
        solution_display: paraview.servermanager.Proxy,
    ) -> None:
        """
        Configure display properties to show the grid in 2d.

        Parameters
        ----------
        render_view
            Render view.
        solution_display
            Solution display.
        """
        if self.show_grid:
            solution_display.SetRepresentationType("Surface With Edges")
        else:
            solution_display.SetRepresentationType("Surface")
        render_view.AxesGrid.Visibility = 1
        render_view.AxesGrid.XTitle = self.grid_labels[0]
        render_view.AxesGrid.YTitle = self.grid_labels[1] + "  "
        render_view.AxesGrid.ZTitle = self.grid_labels[2] + "  "
        # Only show Axes Min-X//Y/Z
        render_view.AxesGrid.AxesToLabel = 7
        # render_view.AxesGrid.FacesToRender = 7
        # Set font family
        render_view.AxesGrid.XTitleFontFamily = self.font_family
        render_view.AxesGrid.YTitleFontFamily = self.font_family
        render_view.AxesGrid.ZTitleFontFamily = self.font_family
        render_view.AxesGrid.XLabelFontFamily = self.font_family
        render_view.AxesGrid.YLabelFontFamily = self.font_family
        render_view.AxesGrid.ZLabelFontFamily = self.font_family
        # Set default font size
        render_view.AxesGrid.XTitleFontSize = self.text_size
        render_view.AxesGrid.YTitleFontSize = self.text_size
        render_view.AxesGrid.ZTitleFontSize = self.text_size
        render_view.AxesGrid.XLabelFontSize = self.label_size
        render_view.AxesGrid.YLabelFontSize = self.label_size
        render_view.AxesGrid.ZLabelFontSize = self.label_size
        # Use gray color for label for good visibility in both light and dark mode
        render_view.AxesGrid.XTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.YTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.ZTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.XLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.YLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.ZLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.GridColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        # scale axes
        solution_display.Scale = list(self.axes_stretch)
        render_view.AxesGrid.DataScale = [
            self.axes_stretch[0] * self.axes_scale[0],
            self.axes_stretch[1] * self.axes_scale[1],
            self.axes_stretch[2] * self.axes_scale[2],
        ]
        # custom labels
        if self.axes_ticks[0] is not None:
            render_view.AxesGrid.XAxisUseCustomLabels = True
            render_view.AxesGrid.XAxisLabels = self.axes_ticks[0]
        if self.axes_ticks[1] is not None:
            render_view.AxesGrid.YAxisUseCustomLabels = True
            render_view.AxesGrid.YAxisLabels = self.axes_ticks[1]
        if self.axes_ticks[2] is not None:
            render_view.AxesGrid.ZAxisUseCustomLabels = True
            render_view.AxesGrid.ZAxisLabels = self.axes_ticks[2]

    def configure_grid_3d(
        self,
        render_view: paraview.servermanager.Proxy,
        solution_display: paraview.servermanager.Proxy,
    ) -> None:
        """
        Configure display properties to show the grid in 3d.

        Parameters
        ----------
        render_view
            Render view.
        solution_display
            Solution display.
        """
        if self.show_grid:
            solution_display.SetRepresentationType("Surface With Edges")
        else:
            solution_display.SetRepresentationType("Surface")
        render_view.AxesGrid.Visibility = 1
        render_view.AxesGrid.XTitle = self.grid_labels[0]
        render_view.AxesGrid.YTitle = " " + self.grid_labels[1] + "  "
        render_view.AxesGrid.ZTitle = " " + self.grid_labels[2] + " "
        # Show all Axes Min/Max-X//Y/Z
        render_view.AxesGrid.AxesToLabel = 63
        # render_view.AxesGrid.FacesToRender = 63
        render_view.AxesGrid.LabelUniqueEdgesOnly = 1
        # Set font family
        render_view.AxesGrid.XTitleFontFamily = self.font_family
        render_view.AxesGrid.YTitleFontFamily = self.font_family
        render_view.AxesGrid.ZTitleFontFamily = self.font_family
        render_view.AxesGrid.XLabelFontFamily = self.font_family
        render_view.AxesGrid.YLabelFontFamily = self.font_family
        render_view.AxesGrid.ZLabelFontFamily = self.font_family
        # Set default font size
        render_view.AxesGrid.XTitleFontSize = self.text_size
        render_view.AxesGrid.YTitleFontSize = self.text_size
        render_view.AxesGrid.ZTitleFontSize = self.text_size
        render_view.AxesGrid.XLabelFontSize = self.label_size
        render_view.AxesGrid.YLabelFontSize = self.label_size
        render_view.AxesGrid.ZLabelFontSize = self.label_size
        # Use gray color for label for good visibility in both light and dark mode
        render_view.AxesGrid.XTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.YTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.ZTitleColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.XLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.YLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.ZLabelColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        render_view.AxesGrid.GridColor = matplotlib.colors.to_rgb(
            self.grid_color
        )
        # scale axes
        solution_display.Scale = list(self.axes_stretch)
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
        color_bar
            Color bar.

        Returns
        -------
        bool
            ``True`` if color bar is visible, ``False`` otherwise.
        """
        color_bar.TitleFontFamily = self.font_family
        color_bar.LabelFontFamily = self.font_family
        color_bar.TitleFontSize = self.text_size
        color_bar.LabelFontSize = self.label_size
        color_bar.TitleColor = matplotlib.colors.to_rgb(self.text_color)
        color_bar.LabelColor = matplotlib.colors.to_rgb(self.text_color)
        if self.color_bar_label_format:
            color_bar.AutomaticLabelFormat = False
            color_bar.LabelFormat = self.color_bar_label_format
        color_bar.AddRangeLabels = self.color_bar_range_labels
        color_bar.RangeLabelFormat = self.color_bar_range_label_format

        if self.color_bar_length == 0:
            return False

        # change scalar bar placement
        color_bar.AutoOrient = False
        color_bar.Orientation = self.color_bar_orientation
        match self.color_bar_position:
            case str():
                color_bar.WindowLocation = self.color_bar_position
            case _:
                color_bar.WindowLocation = "Any Location"
                color_bar.Position = list(self.color_bar_position)
        color_bar.ScalarBarLength = self.color_bar_length
        color_bar.ScalarBarThickness = self.color_bar_thickness

        return True

    def set_style(
        self,
        style: Optional[Literal["None", "notebook", "MNRAS"]] = None,
        preview_size_1d_inches: Optional[tuple[float, float]] = None,
        preview_size_2d_inches: Optional[tuple[float, float]] = None,
        preview_size_3d_inches: Optional[tuple[float, float]] = None,
        font_scale: float = 1.0,
        global_scale: float = 1.0,
        custom_style: Optional[dict[str, Any]] = None,
    ) -> Self:
        """
        Set the ``PlotProperties`` according to a style.

        This can be used to set the style for a specific journal.

        Parameters
        ----------
        style
            Style of to use.

            - ``None``: No style is applied, but scaling can be used
            - ``notebook``: Style optimised for Jupyter notebooks
            - ``MNRAS``: Style for MNRAS article
        preview_size_1d_inches
            Preview window size in 1D in inches.
            Uses a fixed ``dpi`` value to ensure the correct size
            when exporting the view as a pdf.
        preview_size_2d_inches
            Preview window size in 2D in inches.
        preview_size_3d_inches
            Preview window size in 2D in inches.
        font_scale
            Scaling factor for the font in titles, labels and legends.
        global_scale
            Global scaling of the figures.
            This scales the preview size, text size and line widths.
            It can be used to artificially increase the ``dpi``.
        custom_style
            Custom overwrite of PlotProperties, applied after scaling.

        Returns
        -------
        PlotProperties
            Copy of the PlotProperties with the applied style.

        See Also
        --------
        sapphireppplot.utils.set_matplotlib_style:
            Set the style for  ``matplotlib`` plots.
        sapphireppplot.pvplot.save_view:
            Save views as e.g. ``pdf`` with the applied style
            and matching ``dpi``.
        """
        dpi = 72  # ParaView fixes the dpi when exporting as pdf
        if style is None:
            style = "None"
            if preview_size_1d_inches is None:
                preview_size_1d_inches = (
                    self.preview_size_1d[0] / dpi,
                    self.preview_size_1d[1] / dpi,
                )
            if preview_size_2d_inches is None:
                preview_size_2d_inches = (
                    self.preview_size_2d[0] / dpi,
                    self.preview_size_2d[1] / dpi,
                )
            if preview_size_3d_inches is None:
                preview_size_3d_inches = (
                    self.preview_size_3d[0] / dpi,
                    self.preview_size_3d[1] / dpi,
                )

        plot_properties_styles = {
            "None": {},
            "notebook": {
                "label_size": 11,
                "title_size": 12,
                "text_size": 12,
                "color_bar_thickness": 10,
                "default_line_width": 1.25,
            },
            "MNRAS": {
                "font_family": "Times",
                "text_color": "white",
                "label_size": 7,
                "title_size": 8,
                "text_size": 8,
                "grid_color": "black",
                "color_bar_range_labels": True,
                "color_bar_range_label_format": "%g",
                "color_bar_thickness": 6,
                "default_line_width": 1.0,
            },
        }

        if style in plot_properties_styles.keys():
            plot_properties_style = plot_properties_styles[style]
        else:
            raise KeyError(
                f"Style '{style}' not found. "
                f"Available style: {list(plot_properties_styles.keys())}"
            )

        default_preview_size = {
            "notebook": (6.4, 4.3),
            "MNRAS": (3.26, 2.5),
        }
        if preview_size_1d_inches is None:
            preview_size_1d_inches = default_preview_size[style]
        if preview_size_2d_inches is None:
            preview_size_2d_inches = default_preview_size[style]
        if preview_size_3d_inches is None:
            preview_size_3d_inches = default_preview_size[style]

        plot_properties_style["preview_size_1d"] = (  # type: ignore
            int(preview_size_1d_inches[0] * dpi * global_scale),
            int(preview_size_1d_inches[1] * dpi * global_scale),
        )
        plot_properties_style["preview_size_2d"] = (  # type: ignore
            int(preview_size_2d_inches[0] * dpi * global_scale),
            int(preview_size_2d_inches[1] * dpi * global_scale),
        )
        plot_properties_style["preview_size_3d"] = (  # type: ignore
            int(preview_size_3d_inches[0] * dpi * global_scale),
            int(preview_size_3d_inches[1] * dpi * global_scale),
        )

        if font_scale != 1.0:
            for key in (
                "label_size",
                "title_size",
                "text_size",
            ):
                plot_properties_style[key] = int(  # type: ignore
                    font_scale
                    * plot_properties_style.get(  # type: ignore
                        key, getattr(self, key)
                    )
                )

        if global_scale != 1.0:
            for key in ("default_line_width",):
                plot_properties_style[key] = (  # type: ignore
                    global_scale
                    * plot_properties_style.get(  # type: ignore
                        key, getattr(self, key)
                    )
                )
            for key in (
                "label_size",
                "title_size",
                "text_size",
                "legend_symbol_width",
                "color_bar_thickness",
            ):
                plot_properties_style[key] = int(  # type: ignore
                    global_scale
                    * plot_properties_style.get(  # type: ignore
                        key, getattr(self, key)
                    )
                )

        if custom_style:
            plot_properties_style.update(custom_style)  # type: ignore

        return self.replace(**plot_properties_style)  # type: ignore
