"""Load the solution from files."""

import os
from typing import Optional
import paraview.simple as ps
import paraview.servermanager
import paraview.util

from sapphireppplot.utils import get_results_folder
from sapphireppplot.plot_properties import PlotProperties


def load_solution_vtk(
    results_folder: str,
    base_file_name: str = "solution",
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

    Returns
    -------
    solution : paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.

    Notes
    -----
    The 'TimeArray' property is not set.
    """

    search_pattern = os.path.join(results_folder, base_file_name + "*.vtk")
    vtk_files = paraview.util.Glob(search_pattern)
    if not vtk_files:
        raise FileNotFoundError(
            f"No .vtk files found matching '{search_pattern}'"
        )
    print(f"Load results in '{search_pattern}'")

    # create a new 'Legacy VTK Reader'
    solution = ps.LegacyVTKReader(
        registrationName=base_file_name,
        FileNames=vtk_files,
    )
    solution.UpdatePipelineInformation()
    # if load_arrays:
    #     solution.PointArrayStatus = load_arrays
    # solution.TimeArray = "TIME"
    return solution


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
    solution : paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.
    """

    search_pattern = os.path.join(results_folder, base_file_name + "*.vtu")
    vtu_files = paraview.util.Glob(search_pattern)
    if not vtu_files:
        raise FileNotFoundError(
            f"No .vtu files found matching '{search_pattern}'"
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
    solution : paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.

    Notes
    -----
    The 'TimeArray' property is not set.
    """

    search_pattern = os.path.join(results_folder, base_file_name + "*.pvtu")
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


def load_solution_hdf5_with_xdmf(
    results_folder: str,
    base_file_name: str = "solution",
    load_arrays: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Loads a series of .hdf5 solution files from a XDMF file
    in the specified results folder
    using ParaView's Xdmf3ReaderS.

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
    solution : paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no  matching .xdmf file found in the `results_folder`.

    Notes
    -----
    - The 'TimeArray' property is set to "None".
    """

    search_pattern = os.path.join(results_folder, base_file_name + ".xdmf")
    xdmf_file = paraview.util.Glob(search_pattern)
    if not xdmf_file:
        raise FileNotFoundError(
            f"No .xdmf file found matching '{search_pattern}'"
        )
    print(f"Load results in '{search_pattern}'")

    # create a new 'Xdmf3 Reader S'
    solution = ps.Xdmf3ReaderS(
        registrationName=base_file_name,
        FileName=xdmf_file,
    )
    solution.UpdatePipelineInformation()
    if load_arrays:
        solution.PointArrays = load_arrays
    # solution.TimeArray = "TIME"
    return solution


def scale_time_steps(
    solution: paraview.servermanager.SourceProxy,
    t_start: float = 0.0,
    t_end: float = 1.0,
) -> paraview.servermanager.SourceProxy:
    """
    Scales the time step to match the start and end time.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        Solution without time steps.
    t_start : float, optional
        Simulation start time.
    t_end : float, optional
        Simulation end time.

    Returns
    -------
    solution_temporal_scaled: paraview.servermanager.SourceProxy
        Solution with scaled time steps.
    """

    # create a new 'Temporal Shift Scale'
    solution_temporal_scaled = ps.TemporalShiftScale(
        registrationName="TemporalShiftScale", Input=solution
    )

    num = len(solution.GetProperty("TimestepValues"))
    # Properties modified on solution_temporal_scaled
    solution_temporal_scaled.Scale = (t_end - t_start) / (num - 1)
    solution_temporal_scaled.PreShift = 0
    solution_temporal_scaled.PostShift = t_start

    solution_temporal_scaled.UpdatePipelineInformation()

    return solution_temporal_scaled


def load_solution(
    plot_properties: PlotProperties,
    file_format: str = "vtu",
    path_prefix: str = "",
    base_file_name: str = "solution",
    t_start: float = 0.0,
    t_end: float = 1.0,
) -> tuple[
    str, paraview.servermanager.SourceProxy, paraview.servermanager.Proxy
]:
    """
    Simplified loading of the solution independent of file format.

    This function performs the following steps:
    1. Retrieves the folder containing simulation results.
    2. Loads the solution data from the files in the results folder.
    3. Adds time step information if necessary.
    4. Updates the animation scene to the last available time step.

    Parameters
    ----------
    plot_properties : PlotProperties
        Properties of the solution to load.
    file_format : str, optional
        Format of the solution files.
    path_prefix : str, optional
        Prefix for relative path.
    base_file_name : str, optional
        Base name of the solutions files.
    t_start : float, optional
        Simulation start time.
    t_end : float, optional
        Simulation end time.

    Returns
    -------
    results_folder : str
        The path to the results folder.
    solution : paraview.servermanager.SourceProxy
        A ParaView reader object with selected point arrays enabled.
    animation_scene : paraview.servermanager.Proxy
        The ParaView AnimationScene.

    Raises
    ------
    ValueError
        If no matching files are found.
    """

    results_folder = get_results_folder(path_prefix=path_prefix)

    match file_format:
        case "vtk":
            solution_without_time = load_solution_vtk(
                results_folder,
                base_file_name=base_file_name,
            )
            solution = scale_time_steps(
                solution_without_time,
                t_start=t_start,
                t_end=t_end,
            )
        case "vtu":
            solution = load_solution_vtu(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
        case "pvtu":
            solution_without_time = load_solution_pvtu(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
            solution = scale_time_steps(
                solution_without_time,
                t_start=t_start,
                t_end=t_end,
            )
        case "hdf5":
            solution = load_solution_hdf5_with_xdmf(
                results_folder,
                base_file_name=base_file_name,
                load_arrays=plot_properties.series_names,
            )
        case _:
            raise ValueError(f"Unknown file_format: '{file_format}'")

    animation_scene = ps.GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    animation_scene.GoToLast()

    return results_folder, solution, animation_scene
