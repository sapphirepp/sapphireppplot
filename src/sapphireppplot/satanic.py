"""Module for SATANIC (Solving Acceleration, Transport And Non-thermal Interactions in star Clusters) specific plotting."""

from typing import cast, Optional
from collections.abc import Sequence
import numpy as np
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_satanic import PlotPropertiesSatanic
from sapphireppplot.utils import ParamDict
from sapphireppplot.numpyify import DFloatLike
from sapphireppplot import utils, pvload, pvplot, transform, numpyify


def load_solution(
    path_prefix: str = "",
    results_folder: str = "",
    base_file_name: str = "solution",
    animation_time: Optional[float] = None,
    plot_properties_in: Optional[PlotPropertiesSatanic] = None,
) -> tuple[
    str,
    ParamDict,
    paraview.servermanager.SourceProxy,
    paraview.servermanager.Proxy,
    PlotPropertiesSatanic,
]:
    """
    Load solution for SATANIC.

    This function performs the following steps:

    1. Retrieves the folder containing simulation results.
    2. Loads the parameter file.
    3. Loads the solution data from the files in the results folder.
    4. Adds time step information if necessary.
    5. Updates the animation scene to the specified animation time.

    Parameters
    ----------
    path_prefix
        Prefix for relative path.
    results_folder
        The path to the results folder.
    base_file_name
        Base name of the solutions files.
    animation_time
        Set the time at which the animation scene is displayed.
        Defaults to the last time step.
    plot_properties_in
        Properties of the solution.

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
    plot_properties : PlotPropertiesSatanic
        Properties of the solution
        as deduced from the parameters.

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
    if plot_properties_in is None:
        plot_properties_in = PlotPropertiesSatanic()
    plot_properties = plot_properties_in.copy()

    results_folder = utils.get_results_folder(
        path_prefix=path_prefix, results_folder=results_folder
    )

    prm_file = pvload.read_parameter_file(
        results_folder, file_name=base_file_name + "_log.prm"
    )
    prm = utils.prm_to_dict(prm_file)

    plot_properties.dimension = int(prm["dimension"])
    plot_properties.spectral_rescale = float(prm["spectral_rescale"])
    plot_properties.labels[plot_properties.quantity_name] = (
        rf"$p^{plot_properties.spectral_rescale:.0f} f$"
    )

    solution = pvload.load_solution_vtu(
        results_folder,
        base_file_name=base_file_name,
        load_arrays=plot_properties.series_names,
    )

    animation_scene = ps.GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    if animation_time is not None:
        animation_scene.AnimationTime = animation_time
    else:
        animation_scene.GoToLast()

    return results_folder, prm, solution, animation_scene, plot_properties


def to_numpy(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    time_steps: Optional[Sequence[float]] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int, int, int, int], DFloatLike],
]:
    r"""
    Convert time dependent ParaView solution to a numpy array with the data evaluated at the cell centers.

    Parameters
    ----------
    solution
        ParaView solution data.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties of the solution.
    time_steps
        List of time steps to extract the data.
        Defaults to using all time steps.

    Returns
    -------
    t : np.ndarray
        The time steps :math:`t`:
        ``t[n] = t_n``
        where ``n`` is the index of the time step.
    r : np.ndarray
        The radius :math:`r`:
        ``r[i] = r_i``
        where ``i`` is the index of the radius.
    ln_p : np.ndarray
        The logarithmic momentum :math:`\ln(p)`:
        ``ln_p[j] = ln_p_j``
        where ``j`` is the index of the momentum.
    mu : np.ndarray
        The pitch angle :math:`\mu = \cos(\theta)`:
        ``mu[k] = mu_k``
        where ``k`` is the index of the pitch angle.
    f : np.ndarray
        The distribution function :math:`F = p^s f` as a 4D numpy array:
        ``f[n][i][j][k]``.
        The first index ``n`` corresponds to ``t[n]``,
        the second index ``i`` to ``r[i]``,
        the third index ``j`` to ``ln_p[j]``
        and the fourth index ``k`` to ``mu[k]``.

    See Also
    --------
    sapphireppplot.numpify.to_numpy_time_steps_3d : Get numpy arrays.
    """
    t, points, data = numpyify.to_numpy_time_steps_3d(
        solution, animation_scene, [plot_properties.quantity_name], time_steps
    )
    r = points[:, 0, 0, 0]
    ln_p = points[0, :, 0, 1]
    mu = points[0, 0, :, 2]
    f = data[:, 0, :, :, :]

    return t, r, ln_p, mu, f


def plot_f_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesSatanic,
    value_range: Optional[tuple[float, float]] = None,
    log_scale: bool = True,
    show_time: bool = False,
    save_animation: bool = False,
    layout: Optional[paraview.servermanager.ViewLayoutProxy] = None,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of F in 2D.

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
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the y-axes.
    log_scale
        Use a logarithmic color scale?
    show_time
        Display the simulation time in the render view.
    save_animation
        Save an animation of the plot.
    layout
        The layout object where the plot should be added as new view.
        Will create a new one if none if provided.

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
    if not layout:
        layout = ps.CreateLayout(name)
    render_view = pvplot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.quantity_name,
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


def plot_f_over_r(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    ln_p: float = 1.0,
    mu: float = 0.0,
    time: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
]:
    r"""
    Take line-out along :math:`r` of the solution and convert it to numpy.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    ln_p
        The logarithmic momentum :math:`\ln(p)` where to plot the solution.
    mu
        The pitch angle :math:`\mu = \cos(\theta)` where to plot the solution.
    time
        Time at which to extract the solution.
        Defaults to the last time step.
    results_folder
        The directory path where the data will be saved.
    filename
        The base name for the saved data file (without extension).
        If no filename is given, the data and ParaView plot are not saved.

    Returns
    -------
    r : np.ndarray
        The radius :math:`r`.
    f : np.ndarray
        The distribution function :math:`F = p^s f`.

    See Also
    --------
    sapphireppplot.transform.plot_over_line : Create PlotOverLine.
    sapphireppplot.pvplot.plot_line_chart_view : Plot LineChartView.
    sapphireppplot.numpyify.to_numpy_1d : Convert to numpy array.
    """
    if time is None:
        time = cast(float, animation_scene.TimeKeeper.TimestepValues[-1])
    animation_scene.AnimationTime = time

    plot_over_line_r = transform.plot_over_line(
        solution,
        direction="x",
        offset=(0.0, ln_p, mu),
        results_folder=results_folder,
        filename=filename,
        plot_properties=plot_properties,
    )

    r, data = numpyify.to_numpy_1d(
        plot_over_line_r,
        array_names=[plot_properties.quantity_name],
        x_direction=0,
        time=time,
    )
    f = data[0]

    if filename:
        layout = ps.CreateLayout("f(r)")
        pvplot.plot_line_chart_view(
            plot_over_line_r,
            layout,
            x_label=plot_properties.grid_labels[0],
            y_label=plot_properties.labels[plot_properties.quantity_name],
            x_array_name="Points_X",
            visible_lines=[plot_properties.quantity_name],
            plot_properties=plot_properties,
        )
        pvplot.save_screenshot(
            layout, results_folder, filename, plot_properties
        )

    return r, f
