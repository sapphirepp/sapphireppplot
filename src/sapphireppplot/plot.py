"""Show plots using ParaView"""

from typing import Optional
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties


def plot_line_chart_view(
    solution: paraview.servermanager.SourceProxy,
    layout_name: str = "LineChartView",
    title: str = "",
    visible_lines: Optional[list[str]] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Creates and configures a line chart view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source to visualize, typically a ParaView data object.
    layout_name : str, optional
        Name of the layout to create for the chart.
    title : str, optional
        Title for the left axis of the chart.
    visible_lines : list[str], optional
        List of series names to display in the chart.
    plot_properties : PlotProperties, optional
        Properties for plotting like the labels.

    Returns
    -------
    layout : paraview.servermanager.LayoutProxy
        The layout object containing the configured chart view.
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """

    # create new layout object
    layout = ps.CreateLayout(name=layout_name)

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
    layout.PreviewMode = [1280, 720]
    # layout/tab size in pixels
    layout.SetSize(1280, 720)

    # Properties modified on solution_display
    solution_display.UseIndexForXAxis = 0
    solution_display.XArrayName = "Points_X"
    plot_properties.set_display_properties_line_chart_view(solution_display)
    if visible_lines:
        solution_display.SeriesVisibility = visible_lines

    return layout, line_chart_view


def plot_render_view_2d(
    solution: paraview.servermanager.SourceProxy,
    quantity: str,
    layout_name: str = "2D RenderView",
    legend_title: str = "",
    value_range: Optional[list[float]] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Creates and configures a 2D render view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source to visualize, typically a ParaView data object.
    quantity : str
        Name of the quantity to plot.
    layout_name : str, optional
        Name of the layout to create for the view.
    legend_title : str, optional
        Title for the color bar legend.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the color bar.
    plot_properties : PlotProperties, optional
        Properties for plotting like the labels.

    Returns
    -------
    layout : paraview.servermanager.LayoutProxy
        The layout object containing the configured render view.
    render_view : paraview.servermanager.RenderViewProxy
        The configured 2D render view.
    """

    # create new layout object
    layout = ps.CreateLayout(name=layout_name)

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
    layout.PreviewMode = [1024, 1024]
    # layout/tab size in pixels
    layout.SetSize(1024, 1024)

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

    transfer_color.ApplyPreset(plot_properties.color_map, True)

    # get color legend/bar for f_000LUT in view render_view
    color_bar = ps.GetScalarBar(transfer_color, render_view)

    # Properties modified on color_bar
    color_bar.Title = legend_title
    color_bar.TitleFontSize = 24
    color_bar.LabelFontSize = 18
    color_bar.TitleColor = [0.5, 0.5, 0.5]
    color_bar.LabelColor = [0.5, 0.5, 0.5]
    # color_bar.TitleColor = [1.0, 1.0, 1.0]
    # color_bar.LabelColor = [1.0, 1.0, 1.0]

    # change scalar bar placement
    color_bar.WindowLocation = "Any Location"
    color_bar.ScalarBarLength = 0.25
    color_bar.Position = [0.65, 0.1]

    return layout, render_view


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
        TransparentBackground=1,
        FrameStride=1,
    )
