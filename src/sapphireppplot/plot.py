"""Show plots using ParaView"""

from typing import Optional
import paraview.simple as ps
import paraview.servermanager


def plot_line_chart_view(
    solution: paraview.servermanager.SourceProxy,
    layout_name: str = "Layout #1",
    title: str = "",
    visible_lines: Optional[list[str]] = None,
    labels: Optional[list[str]] = None,
    colors: Optional[list[str]] = None,
    line_styles: Optional[list[str]] = None,
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
    labels : list[str], optional
        Labels for the series quantities in the chart.
    colors : list[str], optional
        Line colors for the series quantities in the chart.
    line_styles : list[str], optional
        Line styles for the series quantities in the chart.

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
    if labels:
        solution_display.SeriesLabel = labels
    if colors:
        solution_display.SeriesColor = colors
    if line_styles:
        solution_display.SeriesLineStyle = line_styles
    if visible_lines:
        solution_display.SeriesVisibility = visible_lines

    return layout, line_chart_view


def save_screenshot(
    line_chart_view: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
):
    """
    Saves a screenshot of the given line chart view as 'png'.

    Parameters
    ----------
    line_chart_view : paraview.servermanager.ViewLayoutProxy
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    print(f"Save screenshot '{results_folder}/{filename}.png'")
    ps.SaveScreenshot(
        filename=results_folder + "/" + filename + ".png",
        viewOrLayout=line_chart_view,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=1,
    )


def save_animation(
    line_chart_view: paraview.servermanager.ViewLayoutProxy,
    results_folder: str,
    filename: str,
):
    """
    Saves an animation of the given line chart view as series of 'png'.

    Parameters
    ----------
    line_chart_view : paraview.servermanager.ViewLayoutProxy
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    print(f"Save animation '{results_folder}/{filename}.*.png'")
    ps.SaveAnimation(
        filename=results_folder + "/" + filename + ".png",
        viewOrLayout=line_chart_view,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=1,
        FrameStride=1,
    )
