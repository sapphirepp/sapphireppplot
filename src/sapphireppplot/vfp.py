"""Module for VFP specific plotting."""

from typing import Optional
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_vfp import PlotPropertiesVFP
from sapphireppplot.utils import ParamDict
from sapphireppplot import utils, pvload, pvplot, transform


def load_solution(
    plot_properties: PlotPropertiesVFP,
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
    Load solution for VFP module.

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

    if not plot_properties.lms_indices:
        plot_properties.set_expansion_order(
            int(prm["VFP"]["Expansion"]["Expansion order"])
        )

    file_format = prm["Output"]["Format"]
    if not base_file_name:
        base_file_name = prm["Output"]["Base file name"]
    t_start = 0.0
    t_end = float(prm["VFP"]["Time stepping"]["Final time"])

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


def scale_distribution_function(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
    spectral_index: float = 4.0,
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVFP]:
    """
    Scales the distribution function to the desired spectral index :math:`s`.

    This will create a number of calculator objects,
    each scaling one specific lms_index.

    Parameters
    ----------
    solution
        The the data to scale.
    plot_properties_in
        Properties of the source.
    lms_indices
        The list of indices ``[[l_1,m_1,s_1], [l_2,m_2,s_2]]`` to scale.
        Only these indices will be active in the new solution.
    spectral_index
        Spectral index to scale the distributions function f.

    Returns
    -------
    solution_scaled : SourceProxy
        The scaled distribution function :math:`p^s f_{lms}` for lms_indices.
    plot_properties : PlotPropertiesVFP
        Solution properties for the scaled distribution function.
    """
    if lms_indices is None:
        lms_indices = plot_properties_in.lms_indices
    plot_properties = plot_properties_in.copy()
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

    solution_scaled = solution
    for lms_index in lms_indices:
        name_old = plot_properties_in.f_lms_name(lms_index)
        name_new = plot_properties.f_lms_name(lms_index)

        # Add a new 'Calculator' to the pipeline
        solution_scaled = ps.Calculator(
            registrationName=name_new, Input=solution_scaled
        )

        # Properties modified on solution_scaled
        solution_scaled.ResultArrayName = name_new
        solution_scaled.Function = f"{coord_p}^{spectral_index} * {name_old}"
        if plot_properties.scaled_distribution_function:
            solution_scaled.Function = (
                f"{coord_p}^{spectral_index-3} * {name_old}"
            )

        if plot_properties.line_colors:
            plot_properties.line_colors[name_new] = plot_properties.line_colors[
                name_old
            ]

    # solution_scaled.PointArrays = plot_properties.series_names
    solution_scaled.UpdatePipeline()

    return solution_scaled, plot_properties


def merge_input_function_vectors(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesVFP,
    prefix: str = "func_",
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVFP]:
    """
    Merge the magnetic field and velocity field into ParaView vectors.

    This enables the use vector specific functionality,
    e.g. the stream tracer.

    Parameters
    ----------
    solution
        The the data with the vector components as scalars.
    plot_properties_in
        Properties of the source.
    prefix
        Prefix for the ``series_names``.

    Returns
    -------
    solution_scaled : SourceProxy
        Solution with the merged vectors.
    plot_properties : PlotPropertiesVFP
        Solution properties for the merged vectors.

    See Also
    --------
    :ps:`MergeVectorComponents` : ParaView MergeVectorComponents filter.
    """
    plot_properties = plot_properties_in.copy()

    assert (
        plot_properties.debug_input_functions is True
    ), "`debug_input_functions` must be enabled to merge into vectors"
    assert (
        plot_properties.momentum is False
    ), "Merging to vectors only makes sense in pure space dimensions"

    merge_vector_components_b = ps.MergeVectorComponents(
        registrationName="MergeVectorComponentsB", Input=solution
    )
    merge_vector_components_b.XArray = prefix + "B_x"
    merge_vector_components_b.YArray = prefix + "B_y"
    merge_vector_components_b.ZArray = prefix + "B_z"
    merge_vector_components_b.OutputVectorName = prefix + "B"
    plot_properties.series_names += [prefix + "B"]
    plot_properties.labels[prefix + "B"] = r"$B$"
    plot_properties.line_styles[prefix + "B"] = plot_properties.line_styles[
        prefix + "B_x"
    ]

    merge_vector_components_b.UpdatePipeline()

    merge_vector_components_u = ps.MergeVectorComponents(
        registrationName="MergeVectorComponentsU",
        Input=merge_vector_components_b,
    )
    merge_vector_components_u.XArray = prefix + "u_x"
    merge_vector_components_u.YArray = prefix + "u_y"
    merge_vector_components_u.ZArray = prefix + "u_z"
    merge_vector_components_u.OutputVectorName = prefix + "u"
    plot_properties.series_names += [prefix + "u"]
    plot_properties.labels[prefix + "u"] = r"$u$"
    plot_properties.line_styles[prefix + "u"] = plot_properties.line_styles[
        prefix + "u_x"
    ]

    merge_vector_components_u.UpdatePipeline()

    return merge_vector_components_u, plot_properties


def plot_f_lms_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
    x_label: Optional[str] = None,
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of the specified f_lms in 2D.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    lms_indices
        The list of indices ``[[l_1,m_1,s_1], [l_2,m_2,s_2]]`` to plot.
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
    layout : ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : XYChartViewProxy
        The configured XY chart view.

    See Also
    --------
    sapphireppplot.pvplot.plot_line_chart_view : Plot LineChartView.
    """
    if lms_indices is None:
        lms_indices = plot_properties.lms_indices

    if x_label is None:
        if plot_properties.momentum:
            x_label = r"$\ln p$"
        else:
            x_label = r"$x$"

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

    layout = ps.CreateLayout(name)
    line_chart_view = pvplot.plot_line_chart_view(
        solution,
        layout,
        x_label=x_label,
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


def plot_f_lms_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_index: Optional[list[int]] = None,
    prefix: str = "",
    value_range: Optional[list[float]] = None,
    log_scale: bool = True,
    show_time: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of the specified f_lms in 2D.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    lms_index
        The index ``[l,m,s]`` to plot.
    prefix
        Prefix for quantity name.
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
    if lms_index is None:
        lms_index = [0, 0, 0]
    if plot_properties.prefix_numeric and prefix == "":
        prefix = "numeric_"

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = pvplot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.f_lms_name(lms_index, prefix=prefix),
        value_range=value_range,
        log_scale=log_scale,
        plot_properties=plot_properties,
    )

    if show_time:
        pvplot.display_time(render_view, plot_properties=plot_properties)

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

    return layout, render_view


def plot_f_lms_3d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_index: Optional[list[int]] = None,
    prefix: str = "",
    value_range: Optional[list[float]] = None,
    log_scale: bool = True,
    show_time: bool = False,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of the specified f_lms in 3D.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    lms_index
        The index ``[l,m,s]`` to plot.
    prefix
        Prefix for quantity name.
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
        The configured 3D render view.

    See Also
    --------
    sapphireppplot.pvplot.plot_render_view_3d : Plot 3D RenderView.
    sapphireppplot.pvplot.display_time : Display time.
    """
    if lms_index is None:
        lms_index = [0, 0, 0]
    if plot_properties.prefix_numeric and prefix == "":
        prefix = "numeric_"

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = pvplot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.f_lms_name(lms_index, prefix=prefix),
        value_range=value_range,
        log_scale=log_scale,
        plot_properties=plot_properties,
    )

    if show_time:
        pvplot.display_time(render_view, plot_properties=plot_properties)

    pvplot.save_screenshot(layout, results_folder, name, plot_properties)
    if save_animation:
        pvplot.save_animation(layout, results_folder, name, plot_properties)

    return layout, render_view


def plot_f_lms_over_x(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
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
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    lms_indices
        The list of indices ``[[l_1,m_1,s_1], [l_2,m_2,s_2]]`` to plot.
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
    if lms_indices is None:
        lms_indices = plot_properties.lms_indices

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
    match direction:
        case list():
            x_array_name = "arc_length"
        case "x":
            x_array_name = "Points_X"
        case "y":
            x_array_name = "Points_Y"
        case "z":
            x_array_name = "Points_Z"
        case "d":
            x_array_name = "arc_length"
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


def plot_f_lms_over_p(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_indices: Optional[list[list[int]]] = None,
    direction: str | list[list[float]] = "",
    offset: Optional[list[float]] = None,
    x_range: Optional[list[float]] = None,
    value_range: Optional[list[float]] = None,
    log_x_scale: bool = False,
    log_y_scale: bool = True,
    save_animation: bool = False,
) -> tuple[
    paraview.servermanager.SourceProxy,
    paraview.servermanager.ViewLayoutProxy,
    paraview.servermanager.Proxy,
]:
    """
    Take and plot slice along the p direction of the solution.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder
        Path to the folder where results (images/animations) will be saved.
    name
        Name of the layout and image/animation files.
    plot_properties
        Properties for plotting.
    lms_indices
        The list of indices ``[[l_1,m_1,s_1], [l_2,m_2,s_2]]`` to plot.
    direction
        Direction of the line.
    offset
        Offset of the line.
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
    if lms_indices is None:
        lms_indices = plot_properties.lms_indices

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
    match plot_properties.dim_ps:
        case 1:
            if not direction:
                direction = "x"
            x_array_name = "Points_X"
        case 2:
            if not direction:
                direction = "y"
            x_array_name = "Points_Y"
        case 3:
            if not direction:
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
        x_range=x_range,
        offset=offset,
        results_folder=results_folder,
        filename=name,
        plot_properties=plot_properties,
    )

    layout = ps.CreateLayout(name)
    line_chart_view = pvplot.plot_line_chart_view(
        plot_over_line_p,
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

    return plot_over_line_p, layout, line_chart_view
