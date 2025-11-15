"""Convert ParaView data to numpy arrays."""

from typing import Optional
import numpy as np
import paraview.simple as ps
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
    solution
        ParaView solution data.
    array_names
        List of array names that should be extracted.
    x_direction
        The of the x-axes to extract.
    x_min
        If set, only return the data ``x >= x_min``.
    x_max
        If set, only return the data ``x <= x_max``.

    Returns
    -------
    x_values : np.ndarray
        The x vales as ``np.ndarray``.
    data : np.ndarray
        2D array ``data[c][i]`` with the data from the solution.
        The first index ``c`` corresponds to ``array_names[c]``,
        the second index corresponds to the ``x_array[i]``.
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


def to_numpy_point_list(
    solution: paraview.servermanager.SourceProxy,
    array_names: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert data to a numpy arrays with the data evaluated at the cell centers.

    Parameters
    ----------
    solution
        ParaView solution data.
    array_names
        List of array names that should be extracted.

    Returns
    -------
    points : np.ndarray
        The x/y/z-values of the points as a list:
        ``points[i] = [x, y, z]``.
    data : np.ndarray
        2D array ``data[c][i]`` with the data from the solution.
        The first index ``c`` corresponds to ``array_names[c]``,
        the second index to the point ``points[i]``.

    See Also
    --------
    :ps:`CellCenters` : ParaView CellCenters filter.
    :ps:`PointDatatoCellData` : ParaView PointDatatoCellData filter.
    """
    # create a new 'Cell Centers'
    cell_centers = ps.CellCenters(
        registrationName="CellCenters", Input=solution
    )

    # Fetch the data from the cell_centers object
    cell_center_data = paraview.servermanager.Fetch(cell_centers)

    # Get the point array
    points_vtk = cell_center_data.GetPoints()
    # Convert points to numpy array
    points = numpy_support.vtk_to_numpy(points_vtk.GetData())

    # Sort arrays according to x,y,z coordinate
    sorted_indices = np.lexsort((points[:, 2], points[:, 1], points[:, 0]))
    points = points[sorted_indices]

    # create a new 'Point Data to Cell Data'
    cell_values = ps.PointDatatoCellData(
        registrationName="PointDatatoCellData", Input=solution
    )

    # Fetch the data from the cell_values object
    cell_values_data = paraview.servermanager.Fetch(cell_values)

    data = np.empty((len(array_names), points.shape[0]))

    for i, array_name in enumerate(array_names):
        # Get the data array
        array_vtk = cell_values_data.GetCellData().GetArray(array_name)
        # Convert data to numpy array
        array = numpy_support.vtk_to_numpy(array_vtk)
        # Sort data
        data[i] = array[sorted_indices]

    return points, data


def to_numpy_2d(
    solution: paraview.servermanager.SourceProxy,
    array_names: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert 2D data to a numpy array with the data evaluated at the cell centers.

    Parameters
    ----------
    solution
        ParaView solution data.
    array_names
        List of array names that should be extracted.

    Returns
    -------
    points : np.ndarray
        The x/y/z-values of the points organized in a 2D grid:
        ``points[i][j] = [x, y, z]``.
        Sorted so that ``x`` corresponds to ``i`` and ``y`` to ``j``.
    data : np.ndarray
        3D array ``data[c][i][j]`` with the data from the solution.
        The first index ``c`` corresponds to ``array_names[c]``,
        the second index and third corresponds to ``points[i][j]``.

    See Also
    --------
    to_numpy_point_list : Get numpy arrays of data as point list.
    """
    points, data = to_numpy_point_list(solution, array_names)

    # Reshape arrays to 2D arrays
    indices_x = np.argwhere(points[:, 1] == points[0, 1])  # y constant
    indices_y = np.argwhere(points[:, 0] == points[0, 0])  # x constant
    size_x = indices_x.shape[0]
    size_y = indices_y.shape[0]
    points = points.reshape((size_x, size_y, 3))
    data = data.reshape((len(array_names), size_x, size_y))

    return points, data


def to_numpy_3d(
    solution: paraview.servermanager.SourceProxy,
    array_names: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert 3D data to a numpy array with the data evaluated at the cell centers.

    Parameters
    ----------
    solution
        ParaView solution data.
    array_names
        List of array names that should be extracted.

    Returns
    -------
    points : np.ndarray
        The x/y/z-values of the points organized in a 3D grid:
        ``points[i][j][k] = [x, y, z]``.
        Sorted so that ``x`` corresponds to ``i``,
        ``y`` to ``j``
        and ``z`` to ``k``.
    data : np.ndarray
        4D array ``data[c][i][j][k]`` with the data from the solution.
        The first index ``c`` corresponds to ``array_names[c]``,
        the second, third and forth index corresponds to ``points[i][j][k]``.

    See Also
    --------
    to_numpy_point_list : Get numpy arrays of data as point list.
    """
    points, data = to_numpy_point_list(solution, array_names)

    # Reshape arrays to 2D arrays
    indices_x = np.argwhere(
        (points[:, 1] == points[0, 1]) & (points[:, 2] == points[0, 2])
    )  # y,z constant
    indices_y = np.argwhere(
        (points[:, 0] == points[0, 0]) & (points[:, 2] == points[0, 2])
    )  # x,z constant
    indices_z = np.argwhere(
        (points[:, 0] == points[0, 0]) & (points[:, 1] == points[0, 1])
    )  # y,z constant
    size_x = indices_x.shape[0]
    size_y = indices_y.shape[0]
    size_z = indices_z.shape[0]
    points = points.reshape((size_x, size_y, size_z, 3))
    data = data.reshape((len(array_names), size_x, size_y, size_z))

    return points, data
