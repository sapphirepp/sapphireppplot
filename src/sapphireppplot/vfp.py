"""Module for VFP specific plotting"""

from typing import Optional
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_vfp import PlotPropertiesVFP
from sapphireppplot import plot


def plot_f_lms_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    name: str,
    plot_properties: PlotPropertiesVFP,
    lms_index: Optional[list[int]] = None,
    value_range: Optional[list[float]] = None,
    log_scale: bool = True,
    do_save_animation=False,
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
    plot_properties : PlotPropertiesVFP
        Properties for plotting.
    lms_index : list[int], optional
        The index `[l,m,s]` to plot.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    log_scale : bool, optional
        Use a logarithmic color scale?
    do_save_animation : bool, optional
        If True, also saves an animation of the plot.
        Defaults to False.

    Returns
    -------
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    render_view : paraview.servermanager.RenderViewProxy
        The configured 2D render view.
    """
    if lms_index is None:
        lms_index = [0, 0, 0]

    legend_title = plot_properties.f_lms_label(lms_index)

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = plot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.f_lms_name(lms_index),
        legend_title=legend_title,
        value_range=value_range,
        log_scale=log_scale,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, name)
    if do_save_animation:
        plot.save_animation(layout, results_folder, name)

    return layout, render_view
