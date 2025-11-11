"""Module for MHD specific plotting."""

from typing import Optional
import math
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_mhd import PlotPropertiesMHD
from sapphireppplot.utils import ParamDict
from sapphireppplot import utils, pvload, pvplot, transform


def load_solution(
    plot_properties: PlotPropertiesMHD,
    path_prefix: str = "",
    results_folder: str = "",
    base_file_name: str = "",
) -> tuple[
    str,
    ParamDict,
    paraview.servermanager.SourceProxy,
    paraview.servermanager.Proxy,
]:
    """
    Load solution for MHD module.

    This function performs the following steps:

    1. Retrieves the folder containing simulation results.
    2. Loads the parameter file.
    3. Loads the solution data from the files in the results folder.
    4. Adds time step information if necessary.
    5. Updates the animation scene to the last available time step.

    Parameters
    ----------
    plot_properties
        Properties of the solution to load.
    path_prefix
        Prefix for relative path.
    results_folder
        The path to the results folder.
    base_file_name
        Overwrite base name of the solutions files.

    Returns
    -------
    results_folder : str
        The path to the results folder.
    prm : ParamDict
        Dictionary of the parameters.
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.
    animation_scene : Proxy
        The ParaView AnimationScene.

    Raises
    ------
    ValueError
        If no matching files are found.

    See Also
    --------
    sapphireppplot.pvload : Module to load ParaView files.
    sapphireppplot.utils.get_results_folder : Prompt for results folder.
    sapphireppplot.plot_properties.PlotProperties.series_names :
        Series names list to load.
    """
    results_folder = utils.get_results_folder(
        path_prefix=path_prefix, results_folder=results_folder
    )

    prm_file = pvload.read_parameter_file(results_folder)
    prm = utils.prm_to_dict(prm_file)

    file_format = prm["Output"]["Format"]
    if not base_file_name:
        base_file_name = prm["Output"]["Base file name"]
    t_start = 0.0
    t_end = float(prm["MHD"]["Time stepping"]["Final time"])

    match file_format:
        case "vtu":
            solution = pvload.load_solution_vtu(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
        case "pvtu":
            solution_without_time = pvload.load_solution_pvtu(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
            solution = pvload.scale_time_steps(
                solution_without_time,
                t_start=t_start,
                t_end=t_end,
            )
        case "hdf5":
            solution = pvload.load_solution_hdf5_with_xdmf(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
        case _:
            raise ValueError(f"Unknown file_format: '{file_format}'")

    animation_scene = ps.GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    animation_scene.GoToLast()

    return results_folder, prm, solution, animation_scene


def compute_magnetic_pressure(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesMHD,
    gamma: float = 5.0 / 3.0,
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesMHD]:
    """
    Compute magnetic pressure for the solution.

    Parameters
    ----------
    solution
        The the source data.
    plot_properties_in
        Properties of the source.
    gamma
        The adiabatic index.

    Returns
    -------
    calculator : SourceProxy
        Solution with magnetic pressure.
    plot_properties : PlotPropertiesMHD
        Solution properties for the including the magnetic pressure.
    """
    plot_properties = plot_properties_in.copy()

    # Add a new 'Calculator' to the pipeline
    calculator = ps.Calculator(registrationName="P_B", Input=solution)

    # Properties modified on calculator
    calculator.ResultArrayName = "P_B"
    calculator.Function = f"({gamma}-1) * (b_X^2 + b_Y^2)/2"

    if plot_properties.series_names:
        plot_properties.series_names += ["P_B"]
    plot_properties.labels["P_B"] = r"$P_B$"
    if plot_properties.line_styles:
        plot_properties.line_styles["P_B"] = "1"
    if plot_properties.line_colors:
        plot_properties.line_colors["P_B"] = ["0", "0", "0"]

    calculator.UpdatePipeline()

    return calculator, plot_properties


def compute_normalized_magnetic_divergence(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesMHD,
    divergence_type: str = "total",
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesMHD]:
    """
    Compute normalized magnetic divergence for the solution.

    Parameters
    ----------
    solution
        The the source data.
    plot_properties_in
        Properties of the source.
    divergence_type
        ."total", "cells" or "faces" divergence.

    Returns
    -------
    calculator : SourceProxy
        Solution with normalized magnetic divergence.
    plot_properties : PlotPropertiesMHD
        Solution properties for the including the log magnetic divergence.
    """
    plot_properties = plot_properties_in.copy()

    # Fetch data information from the solution
    solution_data = paraview.servermanager.Fetch(solution)
    # Get number of cells
    n_cells = solution_data.GetNumberOfCells()
    n_cells_x = math.sqrt(n_cells)

    solution_bounds = solution_data.GetBounds()
    dx = (solution_bounds[1] - solution_bounds[0]) / n_cells_x

    name = "normalized_magnetic_divergence"
    quantity_in = "magnetic_divergence"
    label = r"\mid \nabla \cdot B \mid / \mid B \mid \Delta x"
    label_postfix = ""

    match divergence_type:
        case "total":
            pass
        case "cells":
            name += "_cells"
            quantity_in += "_cells"
            label_postfix = r"\mid_{\mathrm{Cell}}"
        case "faces":
            name += "_faces"
            quantity_in += "_faces"
            label_postfix = r"\mid_{\mathrm{Face}}"
        case _:
            raise ValueError(f"Unknown case {type}.")

    # Add a new 'Calculator' to the pipeline
    calculator = ps.Calculator(registrationName=name, Input=solution)

    # Properties modified on calculator
    calculator.ResultArrayName = name
    calculator.Function = f"abs({quantity_in}) / sqrt(b_X^2 + b_Y^2) * {dx}"

    if plot_properties.series_names:
        plot_properties.series_names += [name]
    plot_properties.labels[name] = f"${label} {label_postfix}$"
    if plot_properties.line_styles:
        plot_properties.line_styles[name] = "1"
    if plot_properties.line_colors:
        plot_properties.line_colors[name] = ["0", "0", "0"]

    calculator.UpdatePipeline()

    return calculator, plot_properties


def plot_quantities_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties: PlotPropertiesMHD,
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save a visualization of a specified physical quantity in 1D.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    quantities
        List of physical quantity to plot.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
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
    save_animation
        Save an animation of the plot.

    Returns
    -------
    layout : ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : XYChartViewProxy
        The configured XY chart view.

    See Also
    --------
    sapphireppplot.pvplot.plot_line_chart_view : Plot LineChartView.
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
    line_chart_view = pvplot.plot_line_chart_view(
        solution,
        layout,
        y_label=y_label,
        visible_lines=visible_lines,
        x_range=x_range,
        value_range=value_range,
        log_x_scale=log_x_scale,
        log_y_scale=log_y_scale,
        plot_properties=plot_properties,
    )

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

    return layout, line_chart_view


def plot_split_view_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties_in: PlotPropertiesMHD,
    labels: Optional[list[str]] = None,
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = False,
    save_animation: bool = False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Create split plot of with one quantity per line chart plot.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    quantities
        List of physical quantity to plot.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    labels
        Labels for the numeric and projected/interpolated solution.
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
    save_animation
        Save an animation of the plot.

    Returns
    -------
    layout : ViewLayoutProxy
        The layout object used for the plot.

    See Also
    --------
    sapphireppplot.pvplot.plot_line_chart_view : Plot LineChartView.
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
    plot_properties = plot_properties_in.copy()
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
                plot_properties.quantity_name(quantity, "interpol_"): labels[1],
            }

        # The subplots seem to work without the ``hint`` parameter?!
        line_chart_view = pvplot.plot_line_chart_view(
            solution,
            layout,
            y_label=y_label,
            visible_lines=visible_lines,
            x_range=x_range,
            value_range=value_range,
            log_x_scale=log_x_scale,
            log_y_scale=log_y_scale,
            plot_properties=plot_properties,
        )
        line_chart_view.ShowLegend = 0
        if i == 0 and labels:
            line_chart_view.ShowLegend = 1

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

    return layout


def plot_quantity_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    name: str,
    plot_properties: PlotPropertiesMHD,
    value_range: Optional[list[float]] = None,
    log_scale: bool = False,
    show_time: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of specified physical quantity in 2D.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    quantity
        The physical quantity to plot.
    plot_properties
        Properties for plotting.
    name
        Name of the layout and image/animation files.
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the y-axes.
    log_scale
        Use a logarithmic color scale?
    show_time
        Display the simulation time in the render view.
    save_animation
        Save an animation of the plot.

    Returns
    -------
    layout : ViewLayoutProxy
        The layout object used for the plot.
    render_view : RenderViewProxy
        The configured 2D render view.

    See Also
    --------
    sapphireppplot.pvplot.plot_render_view_2d : Plot 2D RenderView.
    sapphireppplot.pvplot.display_time : Display time.
    """
    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = pvplot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.quantity_name(quantity),
        value_range=value_range,
        log_scale=log_scale,
        plot_properties=plot_properties,
    )

    if show_time:
        pvplot.display_time(render_view, plot_properties=plot_properties)

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

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
    x_axes_scale: Optional[float] = None,
    x_label: str = r"$x$",
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.SourceProxy,
    paraview.servermanager.ViewLayoutProxy,
    paraview.servermanager.Proxy,
]:
    """
    Take and plot slice along a spatial dimension of the solution.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    quantities
        List of physical quantity to plot.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    direction
        Direction of the line.
    offset
        Offset of the line.
    x_axes_scale
        Divide the x-axes coordinate by this scale.
    x_label
        Label for the bottom axis of the chart.
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
    save_animation
        Save an animation of the plot.

    Returns
    -------
    plot_over_line_x : SourceProxy
        The PlotOverLine source.
    layout : ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : XYChartViewProxy
        The configured XY chart view.

    See Also
    --------
    sapphireppplot.transform.plot_over_line : Create PlotOverLine.
    sapphireppplot.pvplot.plot_line_chart_view : Plot LineChartView.
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
    match direction:
        case list():
            x_array_name = "arc_length"
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
    if x_axes_scale is not None:
        x_array_name = "scaled_axes"

    plot_over_line_x = transform.plot_over_line(
        solution,
        direction=direction,
        x_range=x_range,
        offset=offset,
        x_axes_scale=x_axes_scale,
        results_folder=results_folder,
        filename=name,
        plot_properties=plot_properties,
    )

    layout = ps.CreateLayout(name)
    line_chart_view = pvplot.plot_line_chart_view(
        plot_over_line_x,
        layout,
        x_label=x_label,
        y_label=y_label,
        x_array_name=x_array_name,
        visible_lines=visible_lines,
        x_range=x_range,
        value_range=value_range,
        log_x_scale=log_x_scale,
        log_y_scale=log_y_scale,
        plot_properties=plot_properties,
    )

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

    return plot_over_line_x, layout, line_chart_view
