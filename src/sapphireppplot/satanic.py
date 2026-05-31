"""Module for SATANIC (Solving Acceleration, Transport And Non-thermal Interactions in star Clusters) specific plotting."""

from typing import cast, Optional
from collections.abc import Iterable, Sequence
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.collections import QuadMesh
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
    plot_properties.update_properties()

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
        The azimuth angle :math:`\mu = \cos(\theta)`:
        ``mu[k] = mu_k``
        where ``k`` is the index of the azimuth angle.
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


def plot_f_3d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesSatanic,
    value_range: Optional[tuple[float, float]] = None,
    log_scale: bool = True,
    camera_direction: Optional[list[float]] = None,
    show_time: bool = False,
    save_animation: bool = False,
    layout: Optional[paraview.servermanager.ViewLayoutProxy] = None,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plot and save visualization of F in 3D.

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
    camera_direction
        Direction of the camera.
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
        The configured 3D render view.

    See Also
    --------
    sapphireppplot.pvplot.plot_render_view_3d : Plot 3D RenderView.
    sapphireppplot.pvplot.display_time : Display time.
    """
    if not layout:
        layout = ps.CreateLayout(name)
    render_view = pvplot.plot_render_view_3d(
        solution,
        layout,
        plot_properties.quantity_name,
        value_range=value_range,
        log_scale=log_scale,
        camera_direction=camera_direction,
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
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
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


def plot_f_over_p(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    r: float = 1.0,
    mu: float = 0.0,
    time: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
]:
    r"""
    Take line-out along :math:`\ln(p)` of the solution and convert it to numpy.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    r
        The radius :math:`r` where to plot the solution.
    mu
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
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
    ln_p : np.ndarray
        The logarithmic momentum :math:`ln_p`.
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

    plot_over_line_p = transform.plot_over_line(
        solution,
        direction="y",
        offset=(r, 0.0, mu),
        results_folder=results_folder,
        filename=filename,
        plot_properties=plot_properties,
    )

    ln_p, data = numpyify.to_numpy_1d(
        plot_over_line_p,
        array_names=[plot_properties.quantity_name],
        x_direction=1,
        time=time,
    )
    f = data[0]

    if filename:
        layout = ps.CreateLayout("f(p)")
        value_range = None
        try:
            value_range = (min(f[f > 0.0]), max(f))
        except ValueError:
            pass
        pvplot.plot_line_chart_view(
            plot_over_line_p,
            layout,
            x_label=plot_properties.grid_labels[1],
            y_label=plot_properties.labels[plot_properties.quantity_name],
            x_array_name="Points_Y",
            value_range=value_range,
            log_y_scale=True,
            visible_lines=[plot_properties.quantity_name],
            plot_properties=plot_properties,
        )
        pvplot.save_screenshot(
            layout, results_folder, filename, plot_properties
        )

    return ln_p, f


def plot_f_over_mu(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    r: float = 1.0,
    ln_p: float = 1.0,
    time: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
]:
    r"""
    Take line-out along :math:`\mu = \cos(\theta)` of the solution and convert it to numpy.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    r
        The radius :math:`r` where to plot the solution.
    ln_p
        The logarithmic momentum :math:`\ln(p)` where to plot the solution.
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
    mu : np.ndarray
        The azimuth angle :math:`\mu = \cos(\theta)`.
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
        direction="z",
        offset=(r, ln_p, 0.0),
        results_folder=results_folder,
        filename=filename,
        plot_properties=plot_properties,
    )

    mu, data = numpyify.to_numpy_1d(
        plot_over_line_r,
        array_names=[plot_properties.quantity_name],
        x_direction=2,
        time=time,
    )
    f = data[0]

    if filename:
        layout = ps.CreateLayout("f(mu)")
        pvplot.plot_line_chart_view(
            plot_over_line_r,
            layout,
            x_label=plot_properties.grid_labels[2],
            y_label=plot_properties.labels[plot_properties.quantity_name],
            x_array_name="Points_Z",
            visible_lines=[plot_properties.quantity_name],
            plot_properties=plot_properties,
        )
        pvplot.save_screenshot(
            layout, results_folder, filename, plot_properties
        )

    return mu, f


def slice_plane_r_p(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    mu: float = 0.0,
    time: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int, int], DFloatLike],
]:
    r"""
    Slice 2D plane in :math:`r -\ln(p)` of the solution and convert it to numpy.

    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    mu
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
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
        The radius :math:`r`:
        ``r[i] = r_i``
        where ``i`` is the index of the radius.
    ln_p : np.ndarray
        The logarithmic momentum :math:`\ln(p)`:
        ``ln_p[j] = ln_p_j``
        where ``j`` is the index of the momentum.
    f : np.ndarray
        The distribution function :math:`F = p^s f` as a 2D numpy array:
        ``f[i][j]``.
        The first index ``i`` corresponds to ``r[i]``
        and the second index ``j`` to ``ln_p[j]``.

    See Also
    --------
    sapphireppplot.transform.slice_plane : Slice 2D plane.
    sapphireppplot.pvplot.plot_render_view_2d : Plot 2D RenderView.
    sapphireppplot.numpyify.to_numpy_3d : Convert to numpy array.
    """
    if time is None:
        time = cast(float, animation_scene.TimeKeeper.TimestepValues[-1])
    animation_scene.AnimationTime = time
    solution.UpdatePipeline(time=time)

    sliced_plane = solution
    assert plot_properties.dimension >= 2, "Cannot slice plane in 1D"
    if plot_properties.dimension == 3:
        sliced_plane = transform.slice_plane(
            solution,
            normal=(0, 0, 1),
            origin=(0.0, 0.0, mu),
            plot_properties=plot_properties,
            crinkle_slice=True,
        )

    points, data = numpyify.to_numpy_3d(
        sliced_plane,
        array_names=[plot_properties.quantity_name],
    )
    r = points[:, 0, 0, 0]
    ln_p = points[0, :, 0, 1]
    f = data[0, :, :, 0]

    if filename:
        layout = ps.CreateLayout("f(r,p)")
        pvplot.plot_render_view_2d(
            sliced_plane,
            layout,
            plot_properties.quantity_name,
            log_scale=True,
            plot_properties=plot_properties,
        )
        pvplot.save_screenshot(
            layout, results_folder, filename, plot_properties
        )

    return r, ln_p, f


def slice_plane_r_mu(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    ln_p: float = 1.0,
    time: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
) -> tuple[
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int], DFloatLike],
    np.ndarray[tuple[int, int], DFloatLike],
]:
    r"""
    Slice 2D plane in :math:`r -\mu` of the solution and convert it to numpy.

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
        The radius :math:`r`:
        ``r[i] = r_i``
        where ``i`` is the index of the radius.
    mu : np.ndarray
        The azimuth angle :math:`\mu = \cos(\theta)`:
        ``mu[k] = mu_k``
        where ``k`` is the index of the azimuth angle.
    f : np.ndarray
        The distribution function :math:`F = p^s f` as a 2D numpy array:
        ``f[i][k]``.
        The first index ``i`` corresponds to ``r[i]``
        and the second index ``k`` to ``mu[k]``.

    See Also
    --------
    sapphireppplot.transform.slice_plane : Slice 2D plane.
    sapphireppplot.pvplot.plot_render_view_2d : Plot 2D RenderView.
    sapphireppplot.numpyify.to_numpy_3d : Convert to numpy array.
    """
    if time is None:
        time = cast(float, animation_scene.TimeKeeper.TimestepValues[-1])
    animation_scene.AnimationTime = time
    solution.UpdatePipeline(time=time)

    assert plot_properties.dimension == 3, "Solution has no mu dependence!"
    sliced_plane = transform.slice_plane(
        solution,
        normal=(0, 1, 0),
        origin=(0.0, ln_p, 0.0),
        plot_properties=plot_properties,
        crinkle_slice=True,
    )

    points, data = numpyify.to_numpy_3d(
        sliced_plane,
        array_names=[plot_properties.quantity_name],
    )
    r = points[:, 0, 0, 0]
    mu = points[0, 0, :, 2]
    f = data[0, :, 0, :]

    if filename:
        layout = ps.CreateLayout("f(r,p)")
        pvplot.plot_render_view_2d(
            sliced_plane,
            layout,
            plot_properties.quantity_name,
            log_scale=True,
            camera_direction=[0.0, 1.0, 0.0],
            plot_properties=plot_properties,
        )
        pvplot.save_screenshot(
            layout, results_folder, filename, plot_properties
        )

    return r, mu, f


def matplot_f_over_r(
    ax: Axes,
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    p_values: Iterable[float],
    mu: float = 0.0,
    time: Optional[float] = None,
    r_normalization: Optional[float] = None,
) -> Axes:
    r"""
    Take line-out along :math:`r` for multiple momenta and plot on the axes.

    Parameters
    ----------
    ax
        Matplotlib axes to add the plots.
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    p_values
        The linear momentum values :math:`p` where to plot the solution.
    mu
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
    time
        Time at which to extract the solution.
        Defaults to the last time step.
    r_normalization
        Radius :math:`r` to normalize the distribution function.

    Returns
    -------
    ax : Axes
        Matplotlib axes to with the plots.

    See Also
    --------
    plot_f_over_r : Create line out using ParaView.
    """
    for p in p_values:
        r, f = plot_f_over_r(
            solution,
            animation_scene,
            plot_properties,
            ln_p=np.log(p),
            mu=mu,
            time=time,
        )
        normalization = 1.0
        if r_normalization is not None:
            index_normalization = utils.find_closest_index(r, r_normalization)
            normalization = f[index_normalization]
        label = rf"$p = {p:.2f} \,$" + plot_properties.unit_p
        if time is not None:
            label += rf", $t = {time:.2f} \,$" + plot_properties.unit_t
        ax.plot(
            r,
            f / normalization,
            marker="x",
            label=label,
        )

    ax.set_xlabel(plot_properties.grid_labels[0])
    y_label = plot_properties.labels[plot_properties.quantity_name]
    if r_normalization is not None:
        y_label += " [normalized]"
    ax.set_ylabel(y_label)
    ax.legend()

    return ax


def matplot_f_over_p(
    ax: Axes,
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    r_values: Iterable[float],
    mu: float = 0.0,
    time: Optional[float] = None,
    p_normalization: Optional[float] = None,
) -> Axes:
    r"""
    Take line-out along :math:`p` for multiple radia and plot on the axes.

    Parameters
    ----------
    ax
        Matplotlib axes to add the plots.
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    r_values
        The radia :math:`r` where to plot the solution.
    mu
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
    time
        Time at which to extract the solution.
        Defaults to the last time step.
    p_normalization
        Momentum :math:`p` to normalize the distribution function.

    Returns
    -------
    ax : Axes
        Matplotlib axes to with the plots.

    See Also
    --------
    plot_f_over_p : Create line out using ParaView.
    """
    for r in r_values:
        ln_p, f = plot_f_over_p(
            solution,
            animation_scene,
            plot_properties,
            r=r,
            mu=mu,
            time=time,
        )
        normalization = 1.0
        if p_normalization is not None:
            index_normalization = utils.find_closest_index(
                ln_p, np.log(p_normalization)
            )
            normalization = f[index_normalization]
        label = rf"$r = {r:.2f} \,$" + plot_properties.unit_r
        if time is not None:
            label += rf", $t = {time:.2f} \,$" + plot_properties.unit_t
        ax.plot(
            np.exp(ln_p),
            f / normalization,
            marker="x",
            label=label,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-2, None)
    ax.set_xlabel(r"$p \,$ / " + plot_properties.unit_p)
    y_label = plot_properties.labels[plot_properties.quantity_name]
    if p_normalization is not None:
        y_label += " [normalized]"
    ax.set_ylabel(y_label)
    ax.legend()

    return ax


def matplot_f_over_mu(
    ax: Axes,
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    r_values: Iterable[float],
    p_values: Iterable[float],
    time: Optional[float] = None,
    mu_normalization: Optional[float] = None,
) -> Axes:
    r"""
    Take line-out along :math:`\mu = \cos(\theta)` for multiple momenta and plot on the axes.

    Parameters
    ----------
    ax
        Matplotlib axes to add the plots.
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    r_values
        The radia :math:`r` where to plot the solution.
    p_values
        The linear momentum values :math:`p` where to plot the solution.
    time
        Time at which to extract the solution.
        Defaults to the last time step.
    mu_normalization
        Azimuth angle :math:`\mu = \cos(\theta)` to normalize the distribution function.

    Returns
    -------
    ax : Axes
        Matplotlib axes to with the plots.

    See Also
    --------
    plot_f_over_mu : Create line out using ParaView.
    """
    for r in r_values:
        for p in p_values:
            mu, f = plot_f_over_mu(
                solution,
                animation_scene,
                plot_properties,
                r=r,
                ln_p=np.log(p),
                time=time,
            )
            normalization = 1.0
            if mu_normalization is not None:
                index_normalization = utils.find_closest_index(
                    mu, mu_normalization
                )
                normalization = f[index_normalization]
            label = rf"$r = {r:.2f} \,$" + plot_properties.unit_r
            label += rf", $p = {p:.2f} \,$" + plot_properties.unit_p
            if time is not None:
                label += rf", $t = {time:.2f} \,$" + plot_properties.unit_t
            ax.plot(
                mu,
                f / normalization,
                marker="x",
                label=label,
            )

    ax.set_xlabel(plot_properties.grid_labels[2])
    y_label = plot_properties.labels[plot_properties.quantity_name]
    if mu_normalization is not None:
        y_label += " [normalized]"
    ax.set_ylabel(y_label)
    ax.legend()

    return ax


def matplot_f_r_p(
    fig: Figure,
    ax: Axes,
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    plot_properties: PlotPropertiesSatanic,
    mu: float = 0.0,
    time: Optional[float] = None,
    value_range: tuple[float, Optional[float]] = (1e-10, None),
) -> tuple[Figure, Axes, QuadMesh]:
    r"""
    Slice 2D plane in :math:`r -\ln(p)` of the solution and plot on the axes.

    Parameters
    ----------
    fig
        Matplotlib figure to add the plot.
    ax
        Matplotlib axes to add the plot.
    solution
        The simulation or computation result containing the data to plot.
    animation_scene
        The ParaView AnimationScene.
    plot_properties
        Properties for plotting.
    mu
        The azimuth angle :math:`\mu = \cos(\theta)` where to plot the solution.
    time
        Time at which to extract the solution.
        Defaults to the last time step.
    value_range
        Minimal (``value_range[0]``)
        and maximal (``value_range[1]``) value for the color bar.

    Returns
    -------
    fig : Figure
        Matplotlib figure with the plot.
    ax : Axes
        Matplotlib axes with the plot.
    cmesh : QuadMesh
        Matplotlib color mesh.

    See Also
    --------
    slice_plane_r_p : Slice plane using ParaView.
    """
    r, ln_p, f = slice_plane_r_p(
        solution,
        animation_scene,
        plot_properties,
        mu=mu,
        time=time,
    )
    p = np.exp(ln_p)
    mesh_r, mesh_p = np.meshgrid(r, p, indexing="ij")

    f[f < value_range[0]] = value_range[0]

    cmesh = ax.pcolormesh(
        mesh_r,
        mesh_p,
        f,
        cmap=plot_properties.matplot_color_map,
        norm="log",
        vmin=value_range[0],
        vmax=value_range[1],
        shading=plot_properties.matplot_shading,
    )

    ax.set_yscale("log")
    ax.set_xlabel(r"$r \,$ / " + plot_properties.unit_r)
    ax.set_ylabel(r"$p \,$ / " + plot_properties.unit_p)

    fig.colorbar(
        cmesh,
        ax=ax,
        orientation="vertical",
        # pad=-0.1,
        label=plot_properties.labels[plot_properties.quantity_name],
    )

    return fig, ax, cmesh
