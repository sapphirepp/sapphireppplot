"""Module for VFP specific plotting"""

from typing import Optional
import copy
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_vfp import PlotPropertiesVFP
from sapphireppplot import plot, transform


def scale_distribution_function(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
    spectral_index: float = 4.0,
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVFP]:
    """
    Scales the distribution function to the desired spectral index $s$.
    This will create a number of calculator objects,
    each scaling one specific lms_index.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The the data to scale.
    plot_properties_in : PlotPropertiesVFP
        Properties of the source.
    lms_indices : list[list[int]], optional
        The list of indices `[[l_1,m_1,s_1], [l_2,m_2,s_2]]` to scale.
        Only these indices will be active in the new solution.
    spectral_index : float, optional
        Spectral index to scale the distributions function f.

    Returns
    -------
    solution_psd : paraview.servermanager.SourceProxy
        The scaled distribution function `p^s f_lms` for lms_indices.
    plot_properties : PlotPropertiesVFP
        Solution properties for the scaled distribution function.
    """
    if lms_indices is None:
        lms_indices = [[0, 0, 0]]
    plot_properties = copy.deepcopy(plot_properties_in)
    plot_properties.scale_by_spectral_index(spectral_index, lms_indices)

    assert plot_properties.momentum is True, "Can only scale p-dependent data"

    coord_p = ""
    match plot_properties.dim_ps:
        case 1:
            coord_p = "coordsX"
        case 2:
            coord_p = "coordsY"
        case 3:
            coord_p = "coordsZ"
        case _:
            assert False
    if plot_properties.logarithmic_p:
        coord_p = f"exp({coord_p})"

    solution_psd = solution
    for lms_index in lms_indices:
        name_old = plot_properties_in.f_lms_name(lms_index)
        name_new = plot_properties.f_lms_name(lms_index)

        # Add a new 'Calculator' to the pipeline
        solution_psd = ps.Calculator(
            registrationName=name_new, Input=solution_psd
        )

        # Properties modified on solution_psd
        solution_psd.ResultArrayName = name_new
        solution_psd.Function = f"{coord_p}^{spectral_index} * {name_old}"

        if plot_properties.line_colors:
            plot_properties.line_colors[name_new] = plot_properties.line_colors[
                name_old
            ]

    # solution_psd.PointArrays = plot_properties.series_names

    return solution_psd, plot_properties


def plot_f_lms_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_index: Optional[list[int]] = None,
    value_range: Optional[list[float]] = None,
    log_scale: bool = True,
    show_time: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plots and saves a visualization of the specified f_lms
    from the solution in 2D.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesVFP
        Properties for plotting.
    lms_index : list[int], optional
        The index `[l,m,s]` to plot.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    log_scale : bool, optional
        Use a logarithmic color scale?
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
    if lms_index is None:
        lms_index = [0, 0, 0]

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = plot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.f_lms_name(lms_index),
        value_range=value_range,
        log_scale=log_scale,
        plot_properties=plot_properties,
    )

    if show_time:
        plot.display_time(render_view, plot_properties=plot_properties)

    plot.save_screenshot(layout, results_folder, name)
    if save_animation:
        plot.save_animation(layout, results_folder, name)

    return layout, render_view


def plot_f_lms_over_x(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
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
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesVFP
        Properties for plotting.
    lms_indices : list[list[int]], optional
        The list of indices `[[l_1,m_1,s_1], [l_2,m_2,s_2]]` to plot.
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
    if lms_indices is None:
        lms_indices = [[0, 0, 0]]

    y_label = plot_properties.f_lms_label(["l", "m", "s"])
    if len(lms_indices) == 1:
        y_label = plot_properties.f_lms_label(lms_indices[0])
    visible_lines = []
    for lms_index in lms_indices:
        if plot_properties.prefix_numeric:
            visible_lines += [plot_properties.f_lms_name(lms_index, "numeric_")]
        else:
            visible_lines += [plot_properties.f_lms_name(lms_index)]
        if plot_properties.project:
            visible_lines += [plot_properties.f_lms_name(lms_index, "project_")]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.f_lms_name(lms_index, "interpol_")
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


def plot_f_lms_over_p(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
    offset: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_y_scale: bool = True,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.SourceProxy,
    paraview.servermanager.ViewLayoutProxy,
    paraview.servermanager.Proxy,
]:
    """
    Takes a slice along the p direction of the solution and plots it.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    name : str
        Name of the layout and image/animation files.
    plot_properties : PlotPropertiesVFP
        Properties for plotting.
    lms_indices : list[list[int]], optional
        The list of indices `[[l_1,m_1,s_1], [l_2,m_2,s_2]]` to plot.
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
    if lms_indices is None:
        lms_indices = [[0, 0, 0]]

    y_label = plot_properties.f_lms_label(["l", "m", "s"])
    if len(lms_indices) == 1:
        y_label = plot_properties.f_lms_label(lms_indices[0])
    visible_lines = []
    for lms_index in lms_indices:
        if plot_properties.prefix_numeric:
            visible_lines += [plot_properties.f_lms_name(lms_index, "numeric_")]
        else:
            visible_lines += [plot_properties.f_lms_name(lms_index)]
        if plot_properties.project:
            visible_lines += [plot_properties.f_lms_name(lms_index, "project_")]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.f_lms_name(lms_index, "interpol_")
            ]

    direction = ""
    x_array_name = ""
    match plot_properties.dim_ps:
        case 1:
            direction = "x"
            x_array_name = "Points_X"
        case 2:
            direction = "y"
            x_array_name = "Points_Y"
        case 3:
            direction = "z"
            x_array_name = "Points_Z"
        case _:
            assert False
    x_label = r"$p$"
    if plot_properties.logarithmic_p:
        x_label = r"$\ln p$"

    plot_over_line_p = transform.plot_over_line(
        solution,
        direction=direction,
        offset=offset,
        results_folder=results_folder,
        filename=name,
        plot_properties=plot_properties,
    )

    layout = ps.CreateLayout(name)
    line_chart_view = plot.plot_line_chart_view(
        plot_over_line_p,
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

    return plot_over_line_p, layout, line_chart_view
