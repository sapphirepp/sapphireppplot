"""Create plots using ParaView."""

from typing import Optional
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties

PARAVIEW_DATA_SERVER_LOCATION = 2


def plot_line_chart_view(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    x_label: str = r"$x$",
    y_label: str = "",
    x_array_name: str = "Points_X",
    visible_lines: Optional[list[str]] = None,
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = False,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Create and configure line chart view in ParaView.

    Parameters
    ----------
    solution
        The data source to visualize, typically a ParaView data object.
    layout
        ParaView layout to use for the plot.
    x_label
        Label for the bottom axis of the chart.
    y_label
        Label for the left axis of the chart.
    x_array_name
        Name of the array ot use as x-axes.
    visible_lines
        List of series names to display in the chart.
    x_range
        Minimal (``x_range[0]``)
        and maximal (``x_range[1]``) value for the x-axes.
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the y-axes.
    log_x_scale
        Use a logarithmic x-scale?
    log_y_scale
        Use a logarithmic y-scale?
    plot_properties
        Properties for plotting like the labels.

    Returns
    -------
    line_chart_view : XYChartViewProxy
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

    if x_range:
        line_chart_view.BottomAxisUseCustomRange = 1
        line_chart_view.BottomAxisRangeMinimum = x_range[0]
        line_chart_view.BottomAxisRangeMaximum = x_range[1]
    if value_range:
        line_chart_view.LeftAxisUseCustomRange = 1
        line_chart_view.LeftAxisRangeMinimum = value_range[0]
        line_chart_view.LeftAxisRangeMaximum = value_range[1]
    if log_x_scale:
        line_chart_view.BottomAxisLogScale = 1
    if log_y_scale:
        line_chart_view.LeftAxisLogScale = 1

    return line_chart_view


def plot_render_view_2d(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    quantity: str,
    value_range: Optional[list[float]] = None,
    log_scale: bool = False,
    camera_direction: Optional[list[float]] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Create and configure 2D render view in ParaView.

    Parameters
    ----------
    solution
        The data source to visualize, typically a ParaView data object.
    layout
        ParaView layout to use for the plot.
    quantity
        Name of the quantity to plot.
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the color bar.
    log_scale
        Use a logarithmic color scale?
    camera_direction
        Direction of the camera.
    plot_properties
        Properties for plotting like the labels.

    Returns
    -------
    render_view : RenderViewProxy
        The configured 2D render view.

    See Also
    --------
    :pv:`paraview.simple.ResetCameraToDirection <paraview.simple.html#paraview.simple.ResetCameraToDirection>` :
        ParaView method to set camera direction.
    """
    # Create a new 'Render View'
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

    ps.ResetCameraToDirection(direction=camera_direction, view=render_view)

    # reset view to fit data
    render_view.ResetCamera(*plot_properties.camera_view_2d)

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

    plot_properties.configure_grid_2d(render_view, solution_display)

    # reset view to fit data
    render_view.ResetCamera(*plot_properties.camera_view_2d)

    # update the view to ensure updated data information
    render_view.Update()

    vec_component = ""
    base_quantity = quantity
    if quantity.endswith("_X"):
        vec_component = "X"
        base_quantity = quantity.removesuffix("_X")
    if quantity.endswith("_Y"):
        vec_component = "Y"
        base_quantity = quantity.removesuffix("_Y")
    if quantity.endswith("_Z"):
        vec_component = "Z"
        base_quantity = quantity.removesuffix("_Z")

    # set scalar coloring
    ps.ColorBy(
        solution_display,
        (plot_properties.data_type, base_quantity, vec_component),
    )

    # region Configure color bar
    # show color bar/color legend
    solution_display.SetScalarBarVisibility(render_view, True)

    # get color transfer function/color map
    transfer_color = ps.GetColorTransferFunction(base_quantity)
    # get opacity transfer function/opacity map
    transfer_opacity = ps.GetOpacityTransferFunction(base_quantity)
    # get 2D transfer function
    transfer_function = ps.GetTransferFunction2D(base_quantity)

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

    # get color bar
    color_bar = ps.GetScalarBar(transfer_color, render_view)

    # Properties modified on color_bar
    if quantity in plot_properties.labels.keys():
        color_bar.Title = plot_properties.labels[quantity]
    else:
        color_bar.Title = quantity
    color_bar.ComponentTitle = ""
    color_bar_visible = plot_properties.configure_color_bar(color_bar)
    solution_display.SetScalarBarVisibility(render_view, color_bar_visible)
    # endregion

    return render_view


def plot_render_view_3d(
    solution: paraview.servermanager.SourceProxy,
    layout: paraview.servermanager.ViewLayoutProxy,
    quantity: str,
    value_range: Optional[list[float]] = None,
    log_scale: bool = False,
    camera_direction: Optional[list[float]] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Create and configure 3D render view in ParaView.

    Parameters
    ----------
    solution
        The data source to visualize, typically a ParaView data object.
    layout
        ParaView layout to use for the plot.
    quantity
        Name of the quantity to plot.
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the color bar.
    log_scale
        Use a logarithmic color scale?
    camera_direction
        Direction of the camera.
        Uses isometric view by default.
    plot_properties
        Properties for plotting like the labels.

    Returns
    -------
    render_view : RenderViewProxy
        The configured 3D render view.

    See Also
    --------
    :pv:`paraview.simple.ResetCameraToDirection <paraview.simple.html#paraview.simple.ResetCameraToDirection>` :
        ParaView method to set camera direction.
    """
    # Create a new 'Render View'
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
    layout.PreviewMode = plot_properties.preview_size_3d
    # layout/tab size in pixels
    layout.SetSize(
        plot_properties.preview_size_3d[0], plot_properties.preview_size_3d[1]
    )

    # update the view to ensure updated data information
    render_view.Update()

    if camera_direction:
        ps.ResetCameraToDirection(direction=camera_direction, view=render_view)
    else:
        render_view.ApplyIsometricView()

    # reset view to fit data
    render_view.ResetCamera(*plot_properties.camera_view_3d)

    # Hide orientation axes
    render_view.OrientationAxesVisibility = 0

    # changing interaction mode based on data extents
    render_view.InteractionMode = "3D"

    # Properties modified on render_view
    render_view.UseColorPaletteForBackground = 0
    render_view.BackgroundColorMode = "Single Color"
    render_view.Background = [1.0, 1.0, 1.0]

    # Properties modified on solution_display
    solution_display.DisableLighting = 1
    solution_display.Diffuse = 1.0

    plot_properties.configure_grid_3d(render_view, solution_display)

    # reset view to fit data
    render_view.ResetCamera(*plot_properties.camera_view_3d)

    # update the view to ensure updated data information
    render_view.Update()

    vec_component = ""
    base_quantity = quantity
    if quantity.endswith("_X"):
        vec_component = "X"
        base_quantity = quantity.removesuffix("_X")
    if quantity.endswith("_Y"):
        vec_component = "Y"
        base_quantity = quantity.removesuffix("_Y")
    if quantity.endswith("_Z"):
        vec_component = "Z"
        base_quantity = quantity.removesuffix("_Z")

    # set scalar coloring
    ps.ColorBy(
        solution_display,
        (plot_properties.data_type, base_quantity, vec_component),
    )

    # region Configure color bar
    # show color bar/color legend
    solution_display.SetScalarBarVisibility(render_view, True)

    # get color transfer function/color map
    transfer_color = ps.GetColorTransferFunction(base_quantity)
    # get opacity transfer function/opacity map
    transfer_opacity = ps.GetOpacityTransferFunction(base_quantity)
    # get 2D transfer function
    transfer_function = ps.GetTransferFunction2D(base_quantity)

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

    # get color bar
    color_bar = ps.GetScalarBar(transfer_color, render_view)

    # Properties modified on color_bar
    if quantity in plot_properties.labels.keys():
        color_bar.Title = plot_properties.labels[quantity]
    else:
        color_bar.Title = quantity
    color_bar.ComponentTitle = ""
    color_bar_visible = plot_properties.configure_color_bar(color_bar)
    solution_display.SetScalarBarVisibility(render_view, color_bar_visible)
    # endregion

    return render_view


def show_stream_tracer(
    stream_tracer: paraview.servermanager.SourceProxy,
    render_view: paraview.servermanager.Proxy,
    quantity: str | None = None,
    color_bar_visible: bool = False,
    value_range: Optional[list[float]] = None,
    log_scale: bool = False,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Show a stream tracer in a render view in ParaView.

    Parameters
    ----------
    stream_tracer
        The stream tracer to visualize.
    render_view
        ParaView render view in which to show the stream tracer.
    quantity
        Name of the quantity to plot.
        Use ``None`` to display ``Solid Color`` lines.
    color_bar_visible
        Should the color bar be shown?
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the color bar.
    log_scale
        Use a logarithmic color scale?
    plot_properties
        Properties for plotting like the labels.

    Returns
    -------
    render_view : RenderViewProxy
        The configured 2D render view.

    See Also
    --------
    sapphireppplot.transform.stream_tracer : Create stream tracer.
    """
    # set active view
    ps.SetActiveView(render_view)

    # show data in view
    solution_display = ps.Show(
        stream_tracer, render_view, "UnstructuredGridRepresentation"
    )
    # update the view to ensure updated data information
    render_view.Update()

    # set scalar coloring
    ps.ColorBy(solution_display, (plot_properties.data_type, quantity))

    if quantity is None:
        return render_view

    # region Configure color bar
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

    # get color bar
    color_bar = ps.GetScalarBar(transfer_color, render_view)

    # Properties modified on color_bar
    if plot_properties.labels[quantity]:
        color_bar.Title = plot_properties.labels[quantity]
    else:
        color_bar.Title = quantity
    plot_properties.configure_color_bar(color_bar)
    solution_display.SetScalarBarVisibility(render_view, color_bar_visible)
    # endregion

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
    view
        ParaView view to display the text.
    text
        Text to display.
    location
        Text postion.
        Either descriptive string or coordinates.
    plot_properties
        Properties for plotting like the color.

    Returns
    -------
    text_proxy : Proxy
        The text proxy.
    """
    # create a new 'Text'
    text_proxy = ps.Text(registrationName="Text")
    text_proxy.Text = text

    ps.SetActiveSource(text_proxy)

    # show data in view
    text_display = ps.Show(text_proxy, view, "TextSourceRepresentation")

    # Properties modified on text_display
    text_display.FontSize = plot_properties.text_size
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
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.Proxy:
    """
    Display the animation time.

    Parameters
    ----------
    view
        ParaView view to display the text.
    plot_properties
        Properties for plotting like the color.

    Returns
    -------
    annotate_time : Proxy
        The text proxy.
    """
    # create a new 'Annotate Time'
    annotate_time = ps.AnnotateTime(registrationName="AnnotateTime")
    annotate_time.Format = plot_properties.time_format

    ps.SetActiveSource(annotate_time)

    # show data in view
    time_display = ps.Show(annotate_time, view, "TextSourceRepresentation")

    # Properties modified on time_display
    time_display.FontSize = plot_properties.label_size
    time_display.Color = plot_properties.text_color
    match plot_properties.time_location:
        case str():
            time_display.WindowLocation = plot_properties.time_location
        case _:
            time_display.WindowLocation = "Any Location"
            time_display.Position = plot_properties.time_location

    view.Update()
    return annotate_time


def save_screenshot(
    view_or_layout: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
    plot_properties: PlotProperties = PlotProperties(),
) -> None:
    """
    Save screenshot of the given line chart view as ``png``.

    Parameters
    ----------
    view_or_layout
        The ParaView view or layout object to capture in the screenshot.
    results_folder
        The directory path where the screenshot will be saved.
    filename
        The base name for the screenshot file (without extension).
    plot_properties
        Additional properties like background transparency.
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save screenshot '{file_path}")
    ps.SaveScreenshot(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=PARAVIEW_DATA_SERVER_LOCATION,
        TransparentBackground=plot_properties.screenshot_transparent_background,
    )


def save_animation(
    view_or_layout: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
    plot_properties: PlotProperties = PlotProperties(),
) -> None:
    """
    Save animation of the given line chart view as series of ``.png`` files.

    Parameters
    ----------
    view_or_layout
        The ParaView view or layout object to capture in the screenshot.
    results_folder
        The directory path where the screenshot will be saved.
    filename
        The base name for the screenshot file (without extension).
    plot_properties
        Additional properties like background transparency.
    """
    file_path = os.path.join(results_folder, filename + ".png")
    print(f"Save animation '{file_path}")
    ps.SaveAnimation(
        filename=file_path,
        viewOrLayout=view_or_layout,
        location=PARAVIEW_DATA_SERVER_LOCATION,
        TransparentBackground=plot_properties.animation_transparent_background,
        FrameStride=plot_properties.animation_frame_stride,
    )
