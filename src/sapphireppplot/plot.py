"""Show plots using ParaView"""

from typing import Optional
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties


def plot_line_chart_view(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    title: str = "",
    visible_lines: Optional[list[str]] = None,
    value_range: Optional[list[float]] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Creates and configures a line chart view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source to visualize, typically a ParaView data object.
    layout : paraview.servermanager.ViewLayoutProxy
        ParaView layout to use for the plot.
    title : str, optional
        Title for the left axis of the chart.
    visible_lines : list[str], optional
        List of series names to display in the chart.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    plot_properties : PlotProperties, optional
        Properties for plotting like the labels.

    Returns
    -------
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """

    # Create a new 'Line Chart View'
    line_chart_view = ps.CreateView("XYChartView")
    line_chart_view.BottomAxisTitle = "$x$"
    line_chart_view.LeftAxisTitle = title
    line_chart_view.ChartTitleFontSize = 30
    line_chart_view.LeftAxisTitleFontSize = 24
    line_chart_view.BottomAxisTitleFontSize = 24
    line_chart_view.LegendFontSize = 18
    line_chart_view.LeftAxisLabelFontSize = 18
    line_chart_view.BottomAxisLabelFontSize = 18

    # assign view to a particular cell in the layout
    ps.AssignViewToLayout(view=line_chart_view, layout=layout, hint=0)

    # set active view
    ps.SetActiveView(line_chart_view)
    # set active source
    ps.SetActiveSource(solution)

    # show data in view
    solution_display = ps.Show(
        solution, line_chart_view, "XYChartRepresentation"
    )
    # Enter preview mode
    layout.PreviewMode = plot_properties.preview_size_1d
    # layout/tab size in pixels
    layout.SetSize(
        plot_properties.preview_size_1d[0], plot_properties.preview_size_1d[1]
    )

    # Properties modified on solution_display
    solution_display.UseIndexForXAxis = 0
    solution_display.XArrayName = "Points_X"
    plot_properties.set_display_properties_line_chart_view(solution_display)
    if visible_lines:
        solution_display.SeriesVisibility = visible_lines

    if value_range:
        line_chart_view.LeftAxisUseCustomRange = 1
        line_chart_view.LeftAxisRangeMinimum = value_range[0]
        line_chart_view.LeftAxisRangeMaximum = value_range[1]

    return line_chart_view


def plot_render_view_2d(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    quantity: str,
    legend_title: str = "",
    value_range: Optional[list[float]] = None,
    log_scale: bool = False,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Creates and configures a 2D render view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source to visualize, typically a ParaView data object.
    layout : paraview.servermanager.ViewLayoutProxy
        ParaView layout to use for the plot.
    quantity : str
        Name of the quantity to plot.
    legend_title : str, optional
        Title for the color bar legend.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the color bar.
    log_scale : bool, optional
        Use a logarithmic color scale?
    plot_properties : PlotProperties, optional
        Properties for plotting like the labels.

    Returns
    -------
    render_view : paraview.servermanager.RenderViewProxy
        The configured 2D render view.
    """

    # Create a new 'Line Chart View'
    render_view = ps.CreateView("RenderView")

    # assign view to a particular cell in the layout
    ps.AssignViewToLayout(view=render_view, layout=layout, hint=0)

    # set active view
    ps.SetActiveView(render_view)
    # set active source
    ps.SetActiveSource(solution)

    # show data in view
    solution_display = ps.Show(
        solution, render_view, "UnstructuredGridRepresentation"
    )
    # Enter preview mode
    layout.PreviewMode = plot_properties.preview_size_2d
    # layout/tab size in pixels
    layout.SetSize(
        plot_properties.preview_size_2d[0], plot_properties.preview_size_2d[1]
    )

    # update the view to ensure updated data information
    render_view.Update()

    # reset view to fit data
    render_view.ResetCamera(False, 0.9)

    # Hide orientation axes
    render_view.OrientationAxesVisibility = 0

    # changing interaction mode based on data extents
    render_view.InteractionMode = "2D"

    # Properties modified on render_view
    render_view.UseColorPaletteForBackground = 0
    render_view.BackgroundColorMode = "Single Color"
    render_view.Background = [1.0, 1.0, 1.0]

    # Properties modified on solution_display
    solution_display.DisableLighting = 1
    solution_display.Diffuse = 1.0

    plot_properties.show_data_grid(solution_display)

    # update the view to ensure updated data information
    render_view.Update()

    # ----------------------
    # Create color bar plot
    # ----------------------

    # set scalar coloring
    ps.ColorBy(solution_display, (plot_properties.data_type, quantity))

    # show color bar/color legend
    solution_display.SetScalarBarVisibility(render_view, True)

    # get color transfer function/color map
    transfer_color = ps.GetColorTransferFunction(quantity)
    # get opacity transfer function/opacity map
    transfer_opacity = ps.GetOpacityTransferFunction(quantity)
    # get 2D transfer function
    transfer_function = ps.GetTransferFunction2D(quantity)

    # Rescale transfer function
    if value_range:
        transfer_color.RescaleTransferFunction(value_range[0], value_range[1])
        transfer_opacity.RescaleTransferFunction(value_range[0], value_range[1])
        transfer_function.RescaleTransferFunction(
            value_range[0], value_range[1], 0.0, 1.0
        )

    # convert to log space
    if log_scale:
        transfer_color.MapControlPointsToLogSpace()
        transfer_color.UseLogScale = 1

    transfer_color.ApplyPreset(plot_properties.color_map, True)

    # get color legend/bar for f_000LUT in view render_view
    color_bar = ps.GetScalarBar(transfer_color, render_view)

    # Properties modified on color_bar
    color_bar.Title = legend_title
    color_bar_visible = plot_properties.configure_color_bar(color_bar)
    solution_display.SetScalarBarVisibility(render_view, color_bar_visible)

    return render_view


def display_text(
    view: paraview.servermanager.Proxy,
    text: str,
    location: str | list[float] = "Upper Center",
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Display text on a view.

    Parameters
    ----------
    view : paraview.servermanager.Proxy
        ParaView view to display the text.
    text : str
        Text to display.
    location : str | list[float], optional
        Text postion.
        Either descriptive string or coordinates.
    plot_properties : PlotProperties, optional
        Properties for plotting like the color.

    Returns
    -------
    text_proxy : paraview.servermanager.Proxy
        The text proxy.
    """
    # create a new 'Text'
    text_proxy = ps.Text(registrationName="Text")
    text_proxy.Text = text

    ps.SetActiveSource(text_proxy)

    # show data in view
    text_display = ps.Show(text_proxy, view, "TextSourceRepresentation")

    # Properties modified on text_display
    text_display.FontSize = 24
    text_display.Color = plot_properties.text_color
    match location:
        case str():
            text_display.WindowLocation = location
        case _:
            text_display.WindowLocation = "Any Location"
            text_display.Position = location

    view.Update()
    return text_proxy


def display_time(
    view: paraview.servermanager.Proxy,
    time_format: str = r"Time: {time:.2f}",
    location: str | list[float] = "Upper Left Corner",
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Display the animation time.

    Parameters
    ----------
    view : paraview.servermanager.Proxy
        ParaView view to display the text.
    time_format : str, optional
        Formatted text for the time.
    location : str | list[float], optional
        Text postion.
        Either descriptive string or coordinates.
    plot_properties : PlotProperties, optional
        Properties for plotting like the color.

    Returns
    -------
    annotate_time : paraview.servermanager.Proxy
        The text proxy.
    """
    # create a new 'Annotate Time'
    annotate_time = ps.AnnotateTime(registrationName="AnnotateTime")
    annotate_time.Format = time_format

    ps.SetActiveSource(annotate_time)

    # show data in view
    time_display = ps.Show(annotate_time, view, "TextSourceRepresentation")

    # Properties modified on time_display
    time_display.FontSize = 18
    time_display.Color = plot_properties.text_color
    match location:
        case str():
            time_display.WindowLocation = location
        case _:
            time_display.WindowLocation = "Any Location"
            time_display.Position = location

    view.Update()
    return annotate_time


def save_screenshot(
    view_or_layout: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
):
    """
    Saves a screenshot of the given line chart view as 'png'.

    Parameters
    ----------
    view_or_layout : paraview.servermanager.ViewLayoutProxy
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save screenshot '{file_path}")
    ps.SaveScreenshot(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=1,
    )


def save_animation(
    view_or_layout: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
):
    """
    Saves an animation of the given line chart view as series of 'png'.

    Parameters
    ----------
    view_or_layout : paraview.servermanager.ViewLayoutProxy
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save animation '{file_path}")
    ps.SaveAnimation(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=ps.vtkPVSession.DATA_SERVER,
        # For animations it is better to not have transparent background
        TransparentBackground=0,
        FrameStride=1,
    )
