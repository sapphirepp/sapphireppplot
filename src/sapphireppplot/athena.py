"""Module for Athena++ specific plotting."""

import copy
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_athena import PlotPropertiesAthena
from sapphireppplot.utils import ParamDict
from sapphireppplot import utils, pvload


def load_solution(
    plot_properties: PlotPropertiesAthena,  # noqa: U100
    path_prefix: str = "",
    base_file_name: str = "solution",
    results_folder: str = "",
    t_start: float = 0.0,
    t_end: float = 1.0,
) -> tuple[
    str,
    ParamDict,
    paraview.servermanager.SourceProxy,
    paraview.servermanager.Proxy,
]:
    """
    Load athena++ solution.

    This function performs the following steps:

    1. Retrieves the folder containing simulation results.
    2. Loads the solution data from the files in the results folder.
    3. Adds time step information if necessary.
    4. Updates the animation scene to the last available time step.

    Parameters
    ----------
    plot_properties
        Properties of the solution to load.
    path_prefix
        Prefix for relative path.
    results_folder
        The path to the results folder.
    base_file_name
        Base name of the solutions files.
    t_start
        Simulation start time.
    t_end
        Simulation end time.

    Returns
    -------
    results_folder
        The path to the results folder.
    prm
        Dictionary of the parameters.
    solution
        A ParaView reader object with selected point arrays enabled.
    animation_scene
        The ParaView AnimationScene.

    Raises
    ------
    ValueError
        If no matching files are found.
    """
    results_folder = utils.get_results_folder(
        path_prefix=path_prefix, results_folder=results_folder
    )

    prm: ParamDict = {}

    solution_without_time = pvload.load_solution_vtk(
        results_folder,
        base_file_name=base_file_name,
    )
    solution = pvload.scale_time_steps(
        solution_without_time,
        t_start=t_start,
        t_end=t_end,
    )

    animation_scene = ps.GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    animation_scene.GoToLast()

    return results_folder, prm, solution, animation_scene


def compute_magnetic_divergence(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesAthena,
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesAthena]:
    """
    Compute magnetic divergence of the solution.

    Parameters
    ----------
    solution
        The data to calculate the magnetic_convergence on.
    plot_properties_in
        Properties of the source.

    Returns
    -------
    gradient
        The solution with magnetic divergence.
    plot_properties
        Solution properties for the new solution.
    """
    plot_properties = copy.deepcopy(plot_properties_in)

    # create a new 'Gradient'
    gradient = ps.Gradient(registrationName="Gradient", Input=solution)

    # Properties modified on gradient
    gradient.ScalarArray = ["CELLS", "Bcc"]
    gradient.ComputeGradient = 0
    gradient.ComputeDivergence = 1
    gradient.DivergenceArrayName = "magnetic_divergence"

    if plot_properties.series_names:
        plot_properties.series_names += ["magnetic_divergence"]

    gradient.UpdatePipeline()

    return gradient, plot_properties
