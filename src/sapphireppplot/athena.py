"""Module for Athena++ specific plotting"""

import copy
import paraview.simple as ps
import paraview.servermanager

from sapphireppplot.plot_properties_athena import PlotPropertiesAthena


def compute_magnetic_divergence(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesAthena,
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesAthena]:
    """
    Computes the magnetic divergence of the solution.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data to calculate the magnetic_convergence on.
    plot_properties_in : PlotPropertiesAthena
        Properties of the source.

    Returns
    -------
    gradient : paraview.servermanager.SourceProxy
        The solution with magnetic divergence.
    plot_properties : PlotPropertiesVFP
        Solution properties for the new solution.
    """
    plot_properties = copy.deepcopy(plot_properties_in)

    # create a new 'Gradient'
    gradient = ps.Gradient(registrationName='Gradient', Input=solution)

    # Properties modified on gradient
    gradient.ScalarArray = ['CELLS', 'Bcc']
    gradient.ComputeGradient = 0
    gradient.ComputeDivergence = 1
    gradient.DivergenceArrayName = "magnetic_divergence"

    if plot_properties.series_names:
        plot_properties.series_names += ["magnetic_divergence"]

    return gradient, plot_properties
