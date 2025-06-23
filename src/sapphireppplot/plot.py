"""Show plots using ParaView"""

from typing import Optional
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties


def plot_line_chart_view(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    x_label: str = r"$x$",
    y_label: str = "",
    x_array_name: str = "Points_X",
    visible_lines: Optional[list[str]] = None,
    value_range: Optional[list[float]] = None,
    log_y_scale: bool = False,
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
    x_label : str, optional
        Label for the bottom axis of the chart.
    y_label : str, optional
        Label for the left axis of the chart.
    x_array_name : str, optional
        Name of the array ot use as x-axes.
    visible_lines : list[str], optional
        List of series names to display in the chart.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    log_y_scale : bool, optional
        Use a logarithmic y-scale?
    plot_properties : PlotProperties, optional
        Properties for plotting like the labels.

    Returns
    -------
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """

    # Create a new 'Line Chart View'
    line_chart_view = ps.CreateView("XYChartView")
    line_chart_view.BottomAxisTitle = x_label
    line_chart_view.LeftAxisTitle = y_label
    plot_properties.configure_line_chart_view_axes(line_chart_view)

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
    solution_display.XArrayName = x_array_name
    plot_properties.configure_line_chart_view_display(solution_display)
    if visible_lines:
        solution_display.SeriesVisibility = visible_lines

    if value_range:
        line_chart_view.LeftAxisUseCustomRange = 1
        line_chart_view.LeftAxisRangeMinimum = value_range[0]
        line_chart_view.LeftAxisRangeMaximum = value_range[1]
    if log_y_scale:
        line_chart_view.LeftAxisLogScale = 1

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
    text_display.FontSize = plot_properties.title_size
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
    time_display.FontSize = plot_properties.label_size
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
    transparent_background: bool = True,
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
    transparent_background : bool, optional
        Use a transparent background?
        Defaults to `True`.
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save screenshot '{file_path}")
    ps.SaveScreenshot(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=transparent_background,
    )


def save_animation(
    view_or_layout: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
    transparent_background: bool = False,
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
    transparent_background : bool, optional
        Use a transparent background?
        Defaults to `False`.
        For animations it is recommended not to use a transparent background.
        Many formats like `.mp4` do not support it, resulting in artefacts.
        For `.gif` using a transparent background is possible.
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save animation '{file_path}")
    ps.SaveAnimation(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=ps.vtkPVSession.DATA_SERVER,
        # For animations it is better to not have transparent background
        TransparentBackground=transparent_background,
        FrameStride=1,
    )
