"""Convert ParaView data to numpy arrays"""

from typing import Optional
import numpy as np
import paraview.servermanager
from paraview.vtk.util import numpy_support


def to_numpy_1d(
    solution: paraview.servermanager.SourceProxy,
    array_names: list[str],
    x_direction: int = 0,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert 1D data, e.g. from PlotOverLine, to a numpy array.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        ParaView solution data.
    array_names : list[str]
        List of array names that should be extracted.
    x_direction : int, optional
        The of the x-axes to extract.
    x_min : float, optional
        If set, only return the data `x >= x_min`.
    x_max : float, optional
        If set, only return the data `x <= x_max`.

    Returns
    -------
    x_values : np.ndarray
        The x vales as `np.ndarray`.
    data : np.ndarray
        2D array `data[i][j]` with the data from the solution.
        The first index `i` corresponds to `array_names[i]`,
        the second index corresponds to the `x_array[j]`.
    """
    # Fetch the data from the solution
    solution_data = paraview.servermanager.Fetch(solution)

    # Get the points array
    points_vtk = solution_data.GetPoints()
    # Convert points to numpy array
    points = numpy_support.vtk_to_numpy(points_vtk.GetData())
    # Extract x_direction from array
    x_values = points[:, x_direction]

    # Create mask to filter out data between x_min and x_max
    mask = np.ones_like(x_values, dtype=bool)
    if x_min is not None:
        mask &= x_values >= x_min
    if x_max is not None:
        mask &= x_values <= x_max
    x_values = x_values[mask]

    data = np.empty((len(array_names), x_values.size))

    for i, array_name in enumerate(array_names):
        # Get the data array
        array_vtk = solution_data.GetPointData().GetArray(array_name)
        # Convert data to numpy array
        array = numpy_support.vtk_to_numpy(array_vtk)
        # Filter out masked data
        data[i] = array[mask]

    return x_values, data
