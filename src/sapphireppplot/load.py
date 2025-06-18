"""Load the solution from files."""

from typing import Optional
import paraview.simple as ps
import paraview.servermanager
import paraview.util


def load_solution_vtu(
    results_folder: str,
    base_file_name: str = "solution",
    load_arrays: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Loads a series of .vtu solution files from the specified results folder
    using ParaView's XMLUnstructuredGridReader.

    Parameters
    ----------
    results_folder : str
        Path to the folder containing solution_*.pvtu files.
    base_file_name : str, optional
        Base name of the solutions files.
    load_arrays : list[str], optional
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.
    """

    search_pattern = results_folder + "/" + base_file_name + "*.vtu"
    vtu_files = paraview.util.Glob(search_pattern)
    if not vtu_files:
        raise FileNotFoundError(
            f"No .pvtu files found matching '{search_pattern}'"
        )
    print(f"Load results in '{search_pattern}'")

    # create a new 'XML Unstructured Grid Reader'
    solution = ps.XMLUnstructuredGridReader(
        registrationName=base_file_name,
        FileName=vtu_files,
    )
    solution.UpdatePipelineInformation()
    if load_arrays:
        solution.PointArrayStatus = load_arrays
    solution.TimeArray = "TIME"
    return solution


def load_solution_pvtu(
    results_folder: str,
    base_file_name: str = "solution",
    load_arrays: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Loads a series of .pvtu solution files from the specified results folder
    using ParaView's XMLPartitionedUnstructuredGridReader.

    Parameters
    ----------
    results_folder : str
        Path to the folder containing *.pvtu files.
    base_file_name : str, optional
        Base name of the solutions files.
    load_arrays : list[str], optional
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.

    Notes
    -----
    - The 'TimeArray' property is set to "None".
    """

    search_pattern = results_folder + "/" + base_file_name + "*.pvtu"
    pvtu_files = paraview.util.Glob(search_pattern)
    if not pvtu_files:
        raise FileNotFoundError(
            f"No .pvtu files found matching '{search_pattern}'"
        )
    print(f"Load results in '{search_pattern}'")

    # create a new 'XML Partitioned Unstructured Grid Reader'
    solution = ps.XMLPartitionedUnstructuredGridReader(
        registrationName=base_file_name,
        FileName=pvtu_files,
    )
    solution.UpdatePipelineInformation()
    if load_arrays:
        solution.PointArrayStatus = load_arrays
    solution.TimeArray = "None"
    return solution
