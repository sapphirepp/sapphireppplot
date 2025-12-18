"""Load the solution from files using ParaView."""

import os
from typing import Optional
import paraview.simple as ps
import paraview.servermanager
import paraview.util

from sapphireppplot.plot_properties import PlotProperties
from sapphireppplot.utils import ParamDict
from sapphireppplot import utils


def read_parameter_file(
    results_folder: str, file_name: str = "log.prm"
) -> list[str]:
    """
    Read contents of a ``.prm`` parameter file.

    This function utiles the ParaView CSV reader
    to allow reading parameter files on a remote data server.
    It can also be used to read any text file.

    Parameters
    ----------
    results_folder
        Path to the folder containing parameter file.
    file_name
        File name of the parameter file including file extension.
        By default "log.prm".

    Returns
    -------
    prm_lines : list[str]
        List of lines of in the parameter file.

    Raises
    ------
    FileNotFoundError
        If the parameter file is found in the ``results_folder``.
    """
    search_pattern = os.path.join(results_folder, file_name)
    prm_file = paraview.util.Glob(search_pattern)
    if not prm_file:
        raise FileNotFoundError(f"No file found matching '{search_pattern}'")
    print(f"Read file '{search_pattern}'")

    # Use a CSVReader in order to read the text file
    prm_reader = ps.CSVReader(
        registrationName=file_name,
        FileName=prm_file,
        DetectNumericColumns=0,
        UseStringDelimiter=0,
        HaveHeaders=0,
        FieldDelimiterCharacters="",
    )

    prm_data = paraview.servermanager.Fetch(prm_reader)
    col = prm_data.GetColumn(0)

    prm_lines: list[str] = [""] * col.GetNumberOfValues()
    for i in range(col.GetNumberOfValues()):
        prm_lines[i] = col.GetValue(i)

    ps.Delete(prm_reader)
    return prm_lines


def load_csv(
    results_folder: str,
    file_pattern: str = "solution_*.csv",
    delimiter: str = ",",
    have_headers: int = 0,
    skip_lines: int = 0,
    comments: str = "#",
    array_names: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Load contents of a ``.csv`` file as tabular data.

    Parameters
    ----------
    results_folder
        Path to the folder containing ``file_pattern`` files.
    file_pattern
        File pattern of the solutions files.
    delimiter
        Delimiter of the CSV files.
    have_headers
        Treat the first line of the file as headers?
    skip_lines
        Number of lines to skip.
    comments
        Character for comments.
    array_names
        If a list is given, the rows of the table will be renamed accordingly.

    Returns
    -------
    solution : SourceProxy
        A ParaView Source with Row data.

    Raises
    ------
    FileNotFoundError
        If no matching file is found in the ``results_folder``.

    Note
    ----
    Tabular data in ParaView can be converted to point data using
    :ps:`TableToPoints`.
    This point cloud can be converted into a grid using
    :ps:`PointVolumeInterpolator`.
    """
    search_pattern = os.path.join(results_folder, file_pattern)
    csv_files = paraview.util.Glob(search_pattern)
    if not csv_files:
        raise FileNotFoundError(f"No file found matching '{search_pattern}'")
    print(f"Load results in '{search_pattern}'")

    # create a new 'CSV Reader'
    solution = ps.CSVReader(
        registrationName=file_pattern,
        FileName=csv_files,
        DetectNumericColumns=1,
        UseStringDelimiter=1,
        FieldDelimiterCharacters=delimiter,
        HaveHeaders=have_headers,
        SkippedLines=skip_lines,
        CommentCharacters=comments,
    )

    if array_names:
        solution = ps.RenameArrays(
            registrationName="RenameArrays", Input=solution
        )
        name_list = []
        for i, name in enumerate(array_names):
            name_list += [f"Field {i}", name]
        solution.RowArrays = name_list

    solution.UpdatePipelineInformation()
    return solution


def load_solution_vtk(
    results_folder: str,
    base_file_name: str = "solution",
) -> paraview.servermanager.SourceProxy:
    """
    Load series of ``.vtk`` solution files.

    Parameters
    ----------
    results_folder
        Path to the folder containing ``solution_*.vtk`` files.
    base_file_name
        Base name of the solutions files.

    Returns
    -------
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no ``.vtk`` files are found in the ``results_folder``.

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
    Load series of ``.vtu`` solution files.

    Parameters
    ----------
    results_folder
        Path to the folder containing ``solution_*.vtu`` files.
    base_file_name
        Base name of the solutions files.
    load_arrays
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no ``.vtu`` files are found in the ``results_folder``.
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
    Load series of ``.pvtu`` solution files.

    Parameters
    ----------
    results_folder
        Path to the folder containing ``solution_*.pvtu`` files.
    base_file_name
        Base name of the solutions files.
    load_arrays
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no ``.pvtu`` files are found in the ``results_folder``.

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


def load_solution_pvtp(
    results_folder: str,
    base_file_name: str = "solution",
    load_arrays: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Load series of ``.pvtp`` solution files.

    Parameters
    ----------
    results_folder
        Path to the folder containing ``solution_*.pvtp`` files.
    base_file_name
        Base name of the solutions files.
    load_arrays
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no ``.pvtp`` files are found in the ``results_folder``.
    """
    search_pattern = os.path.join(results_folder, base_file_name + "*.pvtp")
    pvtp_files = paraview.util.Glob(search_pattern)
    if not pvtp_files:
        raise FileNotFoundError(
            f"No .pvtp files found matching '{search_pattern}'"
        )
    print(f"Load results in '{search_pattern}'")

    # create a new 'XML Partitioned Unstructured Grid Reader'
    solution = ps.XMLPartitionedPolydataReader(
        registrationName=base_file_name,
        FileName=pvtp_files,
    )
    solution.UpdatePipelineInformation()
    if load_arrays:
        solution.PointArrayStatus = load_arrays
    solution.TimeArray = "TIME"
    return solution


def load_solution_hdf5_with_xdmf(
    results_folder: str,
    base_file_name: str = "solution",
    load_arrays: Optional[list[str]] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Load series of ``.hdf5`` solution files from a ``.xdmf`` file.

    Parameters
    ----------
    results_folder
        Path to the folder containing the ``solution.xdmf`` file.
    base_file_name
        Base name of the solutions files.
    load_arrays
        The name of the arrays in the solution that should be loaded.

    Returns
    -------
    solution : SourceProxy
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no  matching ``.xdmf`` file found in the ``results_folder``.

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
    scale: Optional[float] = None,
) -> paraview.servermanager.SourceProxy:
    """
    Scale time steps to match start and end time.

    Parameters
    ----------
    solution
        Solution without time steps.
    t_start
        Simulation start time.
    t_end
        Simulation end time.
    scale
        Time scaling factor.
        If set, ``t_end`` is ignored and this scaling is used instead.

    Returns
    -------
    solution_temporal_scaled: SourceProxy
        Solution with scaled time steps.
    """
    # create a new 'Temporal Shift Scale'
    solution_temporal_scaled = ps.TemporalShiftScale(
        registrationName="TemporalShiftScale", Input=solution
    )

    num = len(solution.GetProperty("TimestepValues"))
    # Properties modified on solution_temporal_scaled
    solution_temporal_scaled.Scale = (t_end - t_start) / (num - 1)
    if scale:
        solution_temporal_scaled.Scale = scale
    solution_temporal_scaled.PreShift = 0
    solution_temporal_scaled.PostShift = t_start

    # solution_temporal_scaled.UpdatePipelineInformation()
    solution_temporal_scaled.UpdatePipeline()

    return solution_temporal_scaled


def load_solution(
    plot_properties: PlotProperties,
    file_format: str = "vtu",
    path_prefix: str = "",
    base_file_name: str = "solution",
    t_start: float = 0.0,
    t_end: float = 1.0,
    animation_time: Optional[float] = None,
    parameter_file_name: str = "log.prm",
) -> tuple[
    str,
    ParamDict,
    paraview.servermanager.SourceProxy,
    paraview.servermanager.Proxy,
]:
    """
    Simplified loading of the solution independent of file format.

    This function performs the following steps:

    1. Retrieves the folder containing simulation results.
    2. Loads the parameter file.
    3. Loads the solution data from the files in the results folder.
    4. Adds time step information if necessary.
    5. Updates the animation scene to the specified animation time.

    Parameters
    ----------
    plot_properties
        Properties of the solution to load.
    file_format
        Format of the solution files.
    path_prefix
        Prefix for relative path.
    base_file_name
        Base name of the solutions files.
    t_start
        Simulation start time.
    t_end
        Simulation end time.
    animation_time
        Set the time at which the animation scene is displayed.
        Defaults to the last time step.
    parameter_file_name
        File name of the parameter file including file extension.

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
    sapphireppplot.utils.get_results_folder : Prompt for results folder.
    sapphireppplot.plot_properties.PlotProperties.series_names :
        Series names list to load.
    """
    results_folder = utils.get_results_folder(path_prefix=path_prefix)

    prm: ParamDict = {}
    if parameter_file_name:
        try:
            prm_file = read_parameter_file(
                results_folder, file_name=parameter_file_name
            )
            prm = utils.prm_to_dict(prm_file)
        except FileNotFoundError:
            print(
                f"Parameter file `{parameter_file_name}` not found. "
                "Parameter dict is empty."
            )

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
    if animation_time is not None:
        animation_scene.AnimationTime = animation_time
    else:
        animation_scene.GoToLast()

    return results_folder, prm, solution, animation_scene


def load_extract(
    base_file_name: str,
    plot_properties: PlotProperties,
    path_prefix: str = "",
    results_folder: str = "",
    subfolder: str = "extracts",
    animation_time: Optional[float] = None,
    parameter_file_name: str = "log.prm",
) -> tuple[
    str,
    ParamDict,
    paraview.servermanager.SourceProxy,
    paraview.servermanager.Proxy,
]:
    """
    Load extract of a solution.

    This function performs the following steps:

    1. Retrieves the folder containing simulation results.
    2. Loads the parameter file.
    3. Loads the solution data from the files in the results subfolder.
    4. Updates the animation scene to the specified animation time.

    Parameters
    ----------
    base_file_name
        Filename of the extract.
    plot_properties
        Properties of the solution to load.
    path_prefix
        Prefix for relative path.
    results_folder
        The path to the results folder.
    subfolder
        Subfolder with the extracts.
    animation_time
        Set the time at which the animation scene is displayed.
        Defaults to the last time step.
    parameter_file_name
        File name of the parameter file including file extension.

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
    sapphireppplot.utils.get_results_folder : Prompt for results folder.
    sapphireppplot.plot_properties.PlotProperties.series_names :
        Series names list to load.
    sapphireppplot.transform.save_extracts : Save extracts.
    """
    results_folder = utils.get_results_folder(
        path_prefix=path_prefix, results_folder=results_folder
    )

    prm_file = read_parameter_file(
        results_folder, file_name=parameter_file_name
    )
    prm = utils.prm_to_dict(prm_file)

    solution = load_solution_pvtp(
        os.path.join(results_folder, subfolder),
        base_file_name=base_file_name,
        load_arrays=plot_properties.series_names,
    )

    animation_scene = ps.GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    if animation_time is not None:
        animation_scene.AnimationTime = animation_time
    else:
        animation_scene.GoToLast()

    return results_folder, prm, solution, animation_scene
