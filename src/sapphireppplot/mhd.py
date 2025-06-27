"""Module for MHD specific plotting"""

from typing import Optional
import copy
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_mhd import PlotPropertiesMHD
from sapphireppplot import plot, transform


def plot_quantities_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties: PlotPropertiesMHD,
    value_range: Optional[list[float]] = None,
    save_animation: bool = False,
) -> tuple[paraview.servermanager.ViewLayoutProxy,
           paraview.servermanager.Proxy]:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 1D.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantities : list[str]
        List of physical quantity to plot.
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesMHD
        Properties for plotting.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    save_animation : bool, optional
        Save an animation of the plot.

    Returns
    -------
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """
    y_label = r"$\mathbf{w}(x)$"
    if len(quantities) == 1:
        y_label = plot_properties.quantity_label(quantities[0])

    visible_lines = []
    for quantity in quantities:
        if plot_properties.prefix_numeric:
            visible_lines += [
                plot_properties.quantity_name(quantity, "numeric_")
            ]
        else:
            visible_lines += [plot_properties.quantity_name(quantity)]
        if plot_properties.project:
            visible_lines += [
                plot_properties.quantity_name(quantity, "project_")
            ]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.quantity_name(quantity, "interpol_")
            ]

    # create new layout object
    layout = ps.CreateLayout(name)
    line_chart_view = plot.plot_line_chart_view(
        solution,
        layout,
        y_label=y_label,
        visible_lines=visible_lines,
        value_range=value_range,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, name)
    if save_animation:
        plot.save_animation(layout, results_folder, name)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout, line_chart_view


def plot_split_view_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties_in: PlotPropertiesMHD,
    labels: Optional[list[str]] = None,
    value_range: Optional[list[float]] = None,
    save_animation: bool = False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Creates a split plot of with one quantity per line chart plot.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantities : list[str]
        List of physical quantity to plot.
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesMHD
        Properties for plotting.
    labels : Optional[list[str]], optional
        Labels for the numeric and projected/interpolated solution.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    save_animation : bool, optional
        Save an animation of the plot.

    Returns
    -------
    paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    """
    # create new layout object
    layout = ps.CreateLayout(name)

    # split cell
    layout.SplitHorizontal(0, 0.5)
    # layout.SplitVertical(1, 0.5)
    layout.SplitVertical(1, 1.0 / 3.0)
    layout.SplitVertical(4, 0.5)
    # layout.SplitVertical(2, 0.5)
    layout.SplitVertical(2, 1.0 / 3.0)
    layout.SplitVertical(6, 0.5)
    layout.EqualizeViews()

    # Temporarily modify properties
    plot_properties = copy.deepcopy(plot_properties_in)
    # Set all lines black
    for key in plot_properties.line_colors:
        plot_properties.line_colors[key] = ["0", "0", "0"]

    for i, quantity in enumerate(quantities):
        y_label = plot_properties.quantity_label(quantity)

        visible_lines = []
        if plot_properties.prefix_numeric:
            visible_lines += [
                plot_properties.quantity_name(quantity, "numeric_")
            ]
        else:
            visible_lines += [plot_properties.quantity_name(quantity)]
        if plot_properties.project:
            visible_lines += [
                plot_properties.quantity_name(quantity, "project_")
            ]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.quantity_name(quantity, "interpol_")
            ]
        if labels:
            plot_properties.labels = {
                plot_properties.quantity_name(quantity, "numeric_"): labels[0],
                plot_properties.quantity_name(quantity, "project_"): labels[1],
                plot_properties.quantity_name(quantity, "interpol_"):
                labels[1],
            }

        # The subplots seem to work without the `hint` parameter?!
        line_chart_view = plot.plot_line_chart_view(
            solution,
            layout,
            y_label=y_label,
            visible_lines=visible_lines,
            value_range=value_range,
            plot_properties=plot_properties,
        )
        line_chart_view.ShowLegend = 0
        if i == 0 and labels:
            line_chart_view.ShowLegend = 1

    plot.save_screenshot(layout, results_folder, name)
    if save_animation:
        plot.save_animation(layout, results_folder, name)

    return layout


def plot_quantity_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    name: str,
    plot_properties: PlotPropertiesMHD,
    value_range: Optional[list[float]] = None,
    show_time: bool = False,
    save_animation: bool = False,
) -> tuple[paraview.servermanager.ViewLayoutProxy,
           paraview.servermanager.Proxy]:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 2D.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantity : str
        The physical quantity to plot.
    plot_properties : PlotPropertiesMHD
        Properties for plotting.
    name : str
        Name of the layout and image/animation files.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    show_time : bool, optional
        Display the simulation time in the render view.
    save_animation : bool, optional
        Save an animation of the plot.

    Returns
    -------
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    render_view : paraview.servermanager.RenderViewProxy
        The configured 2D render view.
    """

    legend_title = plot_properties.quantity_label(quantity)

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = plot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.quantity_name(quantity),
        legend_title=legend_title,
        value_range=value_range,
        plot_properties=plot_properties,
    )

    if show_time:
        plot.display_time(render_view, plot_properties=plot_properties)

    plot.save_screenshot(layout, results_folder, name)
    if save_animation:
        plot.save_animation(layout, results_folder, name)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout, render_view


def plot_quantities_over_x(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties: PlotPropertiesMHD,
    direction: str | list[list[float]] = "x",
    offset: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_y_scale: bool = False,
    save_animation: bool = False,
) -> tuple[
        paraview.servermanager.SourceProxy,
        paraview.servermanager.ViewLayoutProxy,
        paraview.servermanager.Proxy,
]:
    """
    Takes a slice along a spatial dimension of the solution and plots it.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantities : list[str]
        List of physical quantity to plot.
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesMHD
        Properties for plotting.
    direction : str | list[list[float]]
        Direction of the line.
    offset : list[float], optional
        Offset of the line.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    log_y_scale : bool, optional
        Use a logarithmic y-scale?
    save_animation : bool, optional
        Save an animation of the plot.

    Returns
    -------
    plot_over_line_x : paraview.servermanager.SourceProxy
        The PlotOverLine source.
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """

    y_label = r"$\mathbf{w}(x)$"
    if len(quantities) == 1:
        y_label = plot_properties.quantity_label(quantities[0])

    visible_lines = []
    for quantity in quantities:
        if plot_properties.prefix_numeric:
            visible_lines += [
                plot_properties.quantity_name(quantity, "numeric_")
            ]
        else:
            visible_lines += [plot_properties.quantity_name(quantity)]
        if plot_properties.project:
            visible_lines += [
                plot_properties.quantity_name(quantity, "project_")
            ]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.quantity_name(quantity, "interpol_")
            ]

    x_array_name = ""
    x_label = ""
    match direction:
        case list():
            x_array_name = ""
            x_label = r"$d$"
        case "x":
            x_array_name = "Points_X"
            x_label = r"$x$"
        case "y":
            x_array_name = "Points_Y"
            x_label = r"$y$"
        case "z":
            x_array_name = "Points_Z"
            x_label = r"$z$"
        case "d":
            x_array_name = "arc_length"
            x_label = r"$d$"
        case _:
            raise ValueError(f"Unknown direction {direction}")

    plot_over_line_x = transform.plot_over_line(
        solution,
        direction=direction,
        offset=offset,
        results_folder=results_folder,
        filename=name,
        plot_properties=plot_properties,
    )

    layout = ps.CreateLayout(name)
    line_chart_view = plot.plot_line_chart_view(
        plot_over_line_x,
        layout,
        x_label=x_label,
        y_label=y_label,
        x_array_name=x_array_name,
        visible_lines=visible_lines,
        value_range=value_range,
        log_y_scale=log_y_scale,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, name)
    if save_animation:
        plot.save_animation(layout, results_folder, name)

    return plot_over_line_x, layout, line_chart_view
