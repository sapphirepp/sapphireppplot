"""Transform the solution, e.g. by PlotOverLine or Calculator."""

from typing import Optional, TypeVar, Literal
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties
from sapphireppplot.pvplot import PARAVIEW_DATA_SERVER_LOCATION

_epsilon_d: float = 1e-10
PlotPropertiesVar = TypeVar("PlotPropertiesVar", bound=PlotProperties)


def create_extractor(
    solution: paraview.servermanager.SourceProxy,
    filename: str,
    file_format: Literal["pvtp", "pvtu"] = "pvtp",
    plot_properties: PlotPropertiesVar = PlotProperties(),  # noqa: U100
) -> paraview.servermanager.Proxy:
    """
    Create a extractor of the solution.

    .. important::
       This function only prepares the extracts,
       it does not save them.
       To save the extracts call :py:func:`save_extracts()`.

    This function assumes that the solution is already an extract of the full data,
    e.g. as a result of :py:func:`slice_plane`.

    Parameters
    ----------
    solution
        The extract of the full solution to save.
    filename
        The base name for the extracts (without extension).
    file_format
        Format to save the extract to.
        Use "pvtu" for ``crinkle_slice=True``.
    plot_properties
        Properties of the solution.

    Returns
    -------
    extractor : Proxy
        The extractor to VTP/VTU files.

    Raises
    ------
    ValueError
        If ``file_format`` is not supported.

    See Also
    --------
    :py:func:`sapphireppplot.transform.save_extracts` :
        Save extracts.
    :ps:`ExtractSurface` :
        ParaView ExtractSurface filter.
    :pv:`paraview.simple.CreateExtractor <paraview.simple.__init__.html#paraview.simple.__init__.CreateExtractor>` :
        ParaView filter to save extracts to files.
    """
    if file_format == "pvtp":
        # create a new 'Extract Surface'
        solution = ps.ExtractSurface(
            registrationName="ExtractSurface", Input=solution
        )

    extractor_type = ""
    match file_format:
        case "pvtp":
            extractor_type = "VTP"
        case "pvtu":
            extractor_type = "VTU"
        case _:
            raise ValueError(f"Unknown file_format: '{file_format}'")

    # create extractor
    extractor = ps.CreateExtractor(
        extractor_type, solution, registrationName=extractor_type
    )
    extractor.Enable = 1
    extractor.Writer.FileName = filename + r"_{timestep:06d}." + file_format
    extractor.Writer.FileName
    extractor.Writer.UseSubdirectory = 0
    # extractor.Trigger.Set(
    #     UseEndTimeStep=0,
    #     Frequency=1,
    # )

    return extractor


def save_extracts(
    results_folder: str,
    subfolder: str = "extracts",
    frame_window: Optional[tuple[int, int]] = None,
    plot_properties: PlotPropertiesVar = PlotProperties(),
) -> None:
    """
    Save the extracts of the solution created with :py:func:`create_extractor`.

    Note, this function is expensive as it iterates over all time steps.
    Note, sets the animation time to the last time step.

    Parameters
    ----------
    results_folder
        The parent directory path where the extracts will be saved.
    subfolder
        The subfolder to save the extracts.
    frame_window
        The range of timesteps to extract.
    plot_properties
        Properties of the solution.

    See Also
    --------
    :py:func:`sapphireppplot.transform.create_extractor` :
        Create extracts.
    :pv:`paraview.simple.SaveExtracts <paraview.simple.__init__.html#paraview.simple.__init__.SaveExtracts>` :
        ParaView method to save extracts.
    :py:attr:`sapphireppplot.plot_properties.PlotProperties.extracts_frame_stride` :
        Frame stride.
    """
    file_path = os.path.join(results_folder, subfolder)
    print(f"Save extracts in '{file_path}'")
    if frame_window is not None:
        ps.SaveExtracts(
            ExtractsOutputDirectory=file_path,
            # AnimationScene=animation_scene, # This leads to a segmentation fault
            FrameStride=plot_properties.extracts_frame_stride,
            FrameWindow=frame_window,
        )
    else:
        ps.SaveExtracts(
            ExtractsOutputDirectory=file_path,
            # AnimationScene=animation_scene, # This leads to a segmentation fault
            FrameStride=plot_properties.extracts_frame_stride,
        )


def calculator(
    solution: paraview.servermanager.SourceProxy,
    quantity: str,
    formula: str,
    label: Optional[str] = None,
    plot_properties_in: PlotPropertiesVar = PlotProperties(),
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVar]:
    """
    Create a ParaView Calculator and add the new quantity to the PlotProperties.

    Parameters
    ----------
    solution
        The data source.
    quantity
        Name of the quantity to compute.
    formula
        Formula to compute the quantity as ParaView Function.
    label
        Label for the quantity.
        Default to ``quantity``.
    plot_properties_in
        Properties of the solution.

    Returns
    -------
    calculator_source : SourceProxy
        The calculator source.
    plot_properties : PlotPropertiesVar
        The PlotProperties including the new quantity.

    See Also
    --------
    :ps:`Calculator` : ParaView Calculator filter.
    """
    if not label:
        label = quantity

    plot_properties = plot_properties_in.copy()

    # Add a new 'Calculator' to the pipeline
    calculator_source = ps.Calculator(registrationName=quantity, Input=solution)
    calculator_source.ResultArrayName = quantity
    calculator_source.Function = formula

    if plot_properties.series_names:
        plot_properties.series_names += [quantity]
    plot_properties.labels[quantity] = quantity

    calculator_source.UpdatePipeline()

    return calculator_source, plot_properties


def point_data_to_cell_data(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesVar = PlotProperties(),
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVar]:
    """
    Convert point data to cell data.

    Parameters
    ----------
    solution
        The data source with point data.
    plot_properties_in
        Properties of the solution.

    Returns
    -------
    cell_data : SourceProxy
        The solution as cell data.
    plot_properties : PlotPropertiesVar
        The PlotProperties for the cell data.

    See Also
    --------
    :ps:`PointDatatoCellData` : ParaView filter to convert point data to cell data.
    sapphireppplot.plot_properties.PlotProperties.data_type :
        Solution data type.
    """
    plot_properties = plot_properties_in.copy()

    if plot_properties.data_type == "CELLS":
        return solution, plot_properties

    cell_data = ps.PointDatatoCellData(
        registrationName="PointDatatoCellData", Input=solution
    )
    plot_properties.data_type = "CELLS"

    return cell_data, plot_properties


def plot_over_line(
    solution: paraview.servermanager.SourceProxy,
    direction: str | list[list[float]] = "x",
    offset: Optional[list[float]] = None,
    x_range: Optional[list[float]] = None,
    x_axes_scale: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
    plot_properties: PlotPropertiesVar = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Create and configure plot over line from solution.

    Parameters
    ----------
    solution
        The data source.
    direction
        Direction of the line for the line-out.
        Can be either:

        - ``"x"``, ``"y"``, ``"z"`` for a line along coordinate axes.
        - ``"d"`` for a line along the diagonal.
        - List with start and end points:
          ``[[x_1,y_1,z_1], [x_2,y_2,z_2]]``.
    offset
        Offset of the line-out.
        Only used for ``direction = "x"/"y"/"z"``.
    x_range
        Start (``x_range[0]``) and end-coordinate (``x_range[1]``)
        for line-out along the coordinate axes.
        Only used for ``direction = "x"/"y"/"z"``.
    x_axes_scale
        Divide the x-axes coordinate by this scale.
        The scaled axes will be stored in a variable ``scaled_axes``.
    results_folder
        The directory path where the data will be saved as ``.csv``.
    filename
        The base name for the saved data file (without extension).
        If no filename is given, the data is not saved.
    plot_properties
        Properties of the solution, like the sampling pattern.

    Returns
    -------
    plot_over_line_source : SourceProxy
        The PlotOverLine source.

    See Also
    --------
    :ps:`PlotOverLine` : ParaView PlotOverLine filter.
    sapphireppplot.plot_properties.PlotProperties.sampling_pattern :
        Sampling pattern.
    sapphireppplot.plot_properties.PlotProperties.sampling_resolution :
        Sampling resolution.
    """
    # create a new 'Plot Over Line'
    plot_over_line_source = ps.PlotOverLine(
        registrationName="PlotOverLine", Input=solution
    )

    # Get the bounds in x
    # Fetch data information from the solution
    solution_data = paraview.servermanager.Fetch(solution)
    # Get bounds of the data
    solution_bounds = solution_data.GetBounds()
    if offset is None:
        offset = [0.0, 0.0, 0.0]
    match direction:
        case list():
            plot_over_line_source.Point1 = direction[0]
            plot_over_line_source.Point2 = direction[1]
        case "x":
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]
            if x_range:
                min_x = x_range[0]
                max_x = x_range[1]
            plot_over_line_source.Point1 = [min_x, offset[1], offset[2]]
            plot_over_line_source.Point2 = [max_x, offset[1], offset[2]]
        case "y":
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            if x_range:
                min_y = x_range[0]
                max_y = x_range[1]
            plot_over_line_source.Point1 = [offset[0], min_y, offset[2]]
            plot_over_line_source.Point2 = [offset[0], max_y, offset[2]]
        case "z":
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
            if x_range:
                min_z = x_range[0]
                max_z = x_range[1]
            plot_over_line_source.Point1 = [offset[0], offset[1], min_z]
            plot_over_line_source.Point2 = [offset[0], offset[1], max_z]
        case "d":
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
            plot_over_line_source.Point1 = [min_x, min_y, min_z]
            plot_over_line_source.Point2 = [max_x, max_y, max_z]
        case _:
            raise ValueError(f"Unknown direction {direction}")

    # Change SamplingPattern
    match plot_properties.sampling_pattern:
        case "uniform":
            plot_over_line_source.SamplingPattern = "Sample Uniformly"
            if plot_properties.sampling_resolution:
                plot_over_line_source.Resolution = (
                    plot_properties.sampling_resolution
                )
        case "center":
            plot_over_line_source.SamplingPattern = "Sample At Segment Centers"
            if plot_properties.sampling_resolution:
                plot_over_line_source.ComputeTolerance = False
                plot_over_line_source.Tolerance = (
                    plot_properties.sampling_resolution
                )
        case "boundary":
            plot_over_line_source.SamplingPattern = "Sample At Cell Boundaries"
            if plot_properties.sampling_resolution:
                plot_over_line_source.ComputeTolerance = False
                plot_over_line_source.Tolerance = (
                    plot_properties.sampling_resolution
                )
        case _:
            raise ValueError(
                f"Unknown sampling pattern {plot_properties.sampling_pattern}."
                + "Use one of `uniform`, `center`, `boundary`"
            )

    if x_axes_scale is not None:
        plot_over_line_source = ps.Calculator(
            registrationName="ScaleAxes", Input=plot_over_line_source
        )
        plot_over_line_source.ResultArrayName = "scaled_axes"

        x_array_name = "arc_length"
        match direction:
            case list():
                x_array_name = "arc_length"
            case "x":
                x_array_name = "coordsX"
            case "y":
                x_array_name = "coordsY"
            case "z":
                x_array_name = "coordsZ"
            case "d":
                x_array_name = "arc_length"
            case _:
                raise ValueError(f"Unknown direction {direction}")
        plot_over_line_source.Function = f"{x_array_name} / {x_axes_scale}"

    # Save data if a file is given
    if filename:
        file_path = os.path.join(results_folder, filename + ".csv")
        print(f"Save data '{file_path}'")

        series_names = []
        if plot_properties.series_names:
            series_names += plot_properties.series_names
        if direction == list() or direction == "d":
            series_names += ["arc_length"]
        if x_axes_scale is not None:
            series_names += ["scaled_axes"]

        ps.SaveData(
            filename=file_path,
            proxy=plot_over_line_source,
            location=PARAVIEW_DATA_SERVER_LOCATION,
            ChooseArraysToWrite=(
                1 if plot_properties.series_names is not None else 0
            ),
            PointDataArrays=series_names,
            Precision=5,
            UseScientificNotation=1,
        )

    plot_over_line_source.UpdatePipeline()

    return plot_over_line_source


def slice_plane(
    solution: paraview.servermanager.SourceProxy,
    normal: list[float],
    origin: Optional[list[float]] = None,
    crinkle_slice: bool = False,
    plot_properties: PlotPropertiesVar = PlotProperties(),  # noqa: U100
) -> paraview.servermanager.SourceProxy:
    """
    Slice a 2D plane from a 3D solution.

    Parameters
    ----------
    solution
        The data source.
    normal
        Normal of the plane.
    origin
        Origin of the plane.
        Defaults to ``[0, 0, 0]``.
    crinkle_slice
        This parameter controls whether to extract the entire cells
        that are sliced by the region
        or just extract a triangulated surface of that region.
        If postprocessing is to be done on the data,
        e.g. using the :py:mod:`sapphireppplot.numpyify` module,
        ``crinkle_slice=True`` is recommended.
    plot_properties
        Properties of the solution.

    Returns
    -------
    slice_plane : SourceProxy
        The 2D slice of the solution.

    See Also
    --------
    :ps:`Slice` : ParaView Slice filter.

    Note
    ----
    When using the
    :py:func:`sapphireppplot.pvplot.plot_render_view_2d`
    function to visualize the slice,
    the ``camera_direction`` parameter can be used
    to adjust set the view in the ``normal`` direction.
    """
    if origin is None:
        origin = [0.0, 0.0, 0.0]

    # create a new 'Slice'
    sliced_plane = ps.Slice(registrationName="SlicePlane", Input=solution)

    sliced_plane.Crinkleslice = crinkle_slice
    sliced_plane.SliceType.Normal = normal
    sliced_plane.SliceType.Origin = origin
    # Use small offset to ensure data is within slice plane
    sliced_plane.SliceType.Offset = _epsilon_d

    ps.HideInteractiveWidgets(proxy=sliced_plane.SliceType)
    sliced_plane.UpdatePipeline()

    return sliced_plane


def probe_location(
    solution: paraview.servermanager.SourceProxy,
    point: list[float],
    plot_properties_in: PlotPropertiesVar = PlotProperties(),
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVar]:
    """
    Probe location at one point.

    Parameters
    ----------
    solution
        The data source.
    point
        The point where to evaluate the time evolution.
    plot_properties_in
        Properties of the solution, like the sampling resolution.

    Returns
    -------
    probe_location_source : SourceProxy
        The ProbeLocation source.
    plot_properties : PlotPropertiesVar
        The PlotProperties for ProbeLocation.

    See Also
    --------
    :ps:`ProbeLocation` : ParaView ProbeLocation filter.
    sapphireppplot.plot_properties.PlotProperties.sampling_resolution :
        Sampling resolution.
    """
    plot_properties = plot_properties_in.copy()

    probe_location_source = ps.ProbeLocation(
        registrationName="PointEvaluation",
        Input=solution,
        ProbeType="Fixed Radius Point Source",
    )
    probe_location_source.ProbeType.Center = point
    probe_location_source.ProbeType.Radius = 0
    ps.HideInteractiveWidgets(proxy=probe_location_source.ProbeType)

    if plot_properties.sampling_resolution:
        probe_location_source.ComputeTolerance = False
        probe_location_source.Tolerance = plot_properties.sampling_resolution

    if plot_properties.series_names:
        plot_properties.series_names += ["Point Coordinates"]
    plot_properties.data_type = "POINTS"

    return probe_location_source, plot_properties


def integrate_variables(
    solution: paraview.servermanager.SourceProxy,
    plot_properties_in: PlotPropertiesVar = PlotProperties(),
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVar]:
    """
    Integrate variables over the grid.

    Divide the result by the grid volume.
    For this, the solution is converted to cell data.

    Parameters
    ----------
    solution
        The data source.
    plot_properties_in
        Properties of the solution.

    Returns
    -------
    integrate_variables_source : SourceProxy
        The IntegrateVariables source.
    plot_properties : PlotPropertiesVar
        The PlotProperties for IntegrateVariables.

    See Also
    --------
    :ps:`IntegrateVariables` : ParaView filter to integrate variables.
    point_data_to_cell_data : Convert point data to cell data.
    """
    cell_data, plot_properties = point_data_to_cell_data(
        solution, plot_properties_in=plot_properties_in
    )

    integrate_variables_source = ps.IntegrateVariables(
        registrationName="IntegrateVariables",
        Input=cell_data,
        DivideCellDataByVolume=1,
    )

    if plot_properties.series_names:
        plot_properties.series_names += ["Volume"]
    if plot_properties.labels:
        plot_properties.labels["Volume"] = r"$V$"

    return integrate_variables_source, plot_properties


def plot_over_time(
    solution: paraview.servermanager.SourceProxy,
    t_axes_scale: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
    plot_properties_in: PlotPropertiesVar = PlotProperties(),
) -> tuple[paraview.servermanager.SourceProxy, PlotPropertiesVar]:
    """
    Get temporal evolution of the solution.

    Assumes that the solution only contains one point.
    I.e. that the solution is either a result of
    :py:func:`probe_location`
    or
    :py:func:`integrate_variables`.

    Parameters
    ----------
    solution
        The data source.
        Should one contain one data point.
    t_axes_scale
        Divide the time-axes by this scale.
        The scaled axes will be stored in a variable ``scaled_t_axes``.
    results_folder
        The directory path where the data will be saved as ``.csv``.
    filename
        The base name for the saved data file (without extension).
        If no filename is given, the data is not saved.
    plot_properties_in
        Properties of the solution.

    Returns
    -------
    plot_over_time_source : SourceProxy
        The PlotOverTime source.
    plot_properties : PlotPropertiesVar
        The PlotProperties for PlotOverTime.

    See Also
    --------
    :ps:`PlotDataOverTime` : ParaView PlotDataOverTime filter.
    """
    plot_properties = plot_properties_in.copy()

    plot_over_time_source = ps.PlotDataOverTime(
        registrationName="PlotOverTime",
        Input=solution,
        OnlyReportSelectionStatistics=0,
        FieldAssociation=plot_properties.data_type.capitalize(),
    )
    plot_over_time_source.UpdatePipeline()

    plot_properties.labels = {}
    plot_properties.line_colors = {}
    plot_properties.line_styles = {}
    for key in plot_properties_in.labels.keys():
        plot_properties.labels[key + " (id=0)"] = plot_properties_in.labels[key]
    for key in plot_properties_in.line_colors.keys():
        plot_properties.line_colors[key + " (id=0)"] = (
            plot_properties_in.line_colors[key]
        )
    for key in plot_properties_in.line_styles.keys():
        plot_properties.line_styles[key + " (id=0)"] = (
            plot_properties_in.line_styles[key]
        )

    if plot_properties.series_names:
        plot_properties.series_names += ["Time"]
    if plot_properties.labels:
        plot_properties.labels["Time (id=0)"] = r"$t$"
    plot_properties.bottom_axis_labels = {}
    plot_properties.data_type = "ROWS"

    if t_axes_scale is not None:
        plot_over_time_source = ps.Calculator(
            registrationName="ScaleTimeAxes", Input=plot_over_time_source
        )
        plot_over_time_source.ResultArrayName = "scaled_t_axes"
        plot_over_time_source.ResultTCoords = True

        x_array_name = "Time"
        plot_over_time_source.Function = f"{x_array_name} / {t_axes_scale}"
        plot_over_time_source.UpdatePipeline()

        if plot_properties.series_names:
            plot_properties.series_names += ["scaled_t_axes"]
        if plot_properties.labels:
            plot_properties.labels["scaled_t_axes (id=0)"] = r"$t / t_0$"

    # Save data if a file is given
    if filename:
        file_path = os.path.join(results_folder, filename + ".csv")
        print(f"Save data '{file_path}'")
        ps.SaveData(
            filename=file_path,
            proxy=plot_over_time_source,
            location=PARAVIEW_DATA_SERVER_LOCATION,
            ChooseArraysToWrite=(
                1 if plot_properties.series_names is not None else 0
            ),
            FieldAssociation="Row Data",
            RowDataArrays=plot_properties.series_names,
        )

    return plot_over_time_source, plot_properties


def clip_area(
    solution: paraview.servermanager.SourceProxy,
    min_x: float = -10,
    max_x: float = 10,
    plot_properties: PlotPropertiesVar = PlotProperties(),  # noqa: U100
) -> paraview.servermanager.SourceProxy:
    """
    Clip area from solution.

    Parameters
    ----------
    solution
        The data source.
    min_x
        Start clip at min_x,
    min_x
        End clip at max_x.
    plot_properties
        Properties of the solution, like the sampling pattern.

    Returns
    -------
    clipped_solution : SourceProxy
        The clipped source.

    See Also
    --------
    :ps:`Clip` : ParaView Clip filter.
    """
    clipped_solution = ps.Clip(registrationName="Clip", Input=solution)

    clipped_solution.ClipType = "Box"
    clipped_solution.Crinkleclip = 1

    solution_data = paraview.servermanager.Fetch(solution)
    bounds = solution_data.GetBounds()
    min_y = bounds[2]
    max_y = bounds[3]

    # Use small epsilon in z to capture cells inside box
    clipped_solution.ClipType.Position = [min_x, min_y, -_epsilon_d]
    clipped_solution.ClipType.Length = [
        max_x - min_x,
        max_y - min_y,
        2 * _epsilon_d,
    ]

    ps.HideInteractiveWidgets(proxy=clipped_solution.ClipType)
    clipped_solution.UpdatePipeline()

    return clipped_solution


def stream_tracer(
    solution: paraview.servermanager.SourceProxy,
    quantity: str,
    direction: str | list[list[float]] = "d",
    offset: Optional[list[float]] = None,
    x_range: Optional[list[float]] = None,
    n_lines: int = 30,
    plot_properties: PlotPropertiesVar = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Create stream tracer of a quantity from the solution.

    The ``stream_tracer`` can be added to an existing ``render_view``
    using ``pvplot.show_stream_tracer()``.

    Parameters
    ----------
    solution
        The data source.
    quantity
        Name of the quantity for the stream tracer.
    direction
        Direction of the tracer seed line.
        Can be either:

        - ``"x"``, ``"y"``, ``"z"`` for a line along coordinate axes.
        - ``"d"`` for a line along the diagonal.
        - List with start and end points:
          ``[[x_1,y_1,z_1], [x_2,y_2,z_2]]``.
    offset
        Offset of the tracer seed line.
        Only used for ``direction = "x"/"y"/"z"``.
    x_range
        Start (``x_range[0]``) and end-coordinate (``x_range[1]``)
        for tracer seed line along the coordinate axes.
        Only used for ``direction = "x"/"y"/"z"``.
    n_lines
        Number of stream lines.
    plot_properties
        Properties of the solution.

    Returns
    -------
    stream_tracer_source : SourceProxy
        The StreamTracer source.

    See Also
    --------
    :ps:`StreamTracer` : ParaView StreamTracer filter.
    sapphireppplot.plot_properties.PlotProperties.stream_tracer_maximum_error :
        Maximum error.
    sapphireppplot.plot_properties.PlotProperties.stream_tracer_minimum_step :
        Minimum step length.
    sapphireppplot.plot_properties.PlotProperties.stream_tracer_initial_step :
        Initial step length.
    sapphireppplot.plot_properties.PlotProperties.stream_tracer_maximum_step :
        Maximum step length.
    """
    # create a new 'Stream Tracer'
    stream_tracer_source = ps.StreamTracer(
        registrationName="StreamTracer",
        Input=solution,
        SeedType="Line",
    )
    stream_tracer_source.Vectors = [plot_properties.data_type, quantity]

    # Get the bounds in x
    # Fetch data information from the solution
    solution_data = paraview.servermanager.Fetch(solution)
    # Get bounds of the data
    solution_bounds = solution_data.GetBounds()
    if offset is None:
        offset = [0.0, 0.0, 0.0]
    match direction:
        case list():
            stream_tracer_source.SeedType.Point1 = direction[0]
            stream_tracer_source.SeedType.Point2 = direction[1]
        case "x":
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]
            if x_range:
                min_x = x_range[0]
                max_y = x_range[1]
            stream_tracer_source.SeedType.Point1 = [min_x, offset[1], offset[2]]
            stream_tracer_source.SeedType.Point2 = [max_x, offset[1], offset[2]]
        case "y":
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            if x_range:
                min_y = x_range[0]
                max_y = x_range[1]
            stream_tracer_source.SeedType.Point1 = [offset[0], min_y, offset[2]]
            stream_tracer_source.SeedType.Point2 = [offset[0], max_y, offset[2]]
        case "z":
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
            if x_range:
                min_z = x_range[0]
                max_z = x_range[1]
            stream_tracer_source.SeedType.Point1 = [offset[0], offset[1], min_z]
            stream_tracer_source.SeedType.Point2 = [offset[0], offset[1], max_z]
        case "d":
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
            stream_tracer_source.SeedType.Point1 = [min_x, min_y, min_z]
            stream_tracer_source.SeedType.Point2 = [max_x, max_y, max_z]
        case _:
            raise ValueError(f"Unknown direction {direction}")

    stream_tracer_source.SeedType.Resolution = n_lines

    stream_tracer_source.MaximumError = (
        plot_properties.stream_tracer_maximum_error
    )
    stream_tracer_source.MinimumStepLength = (
        plot_properties.stream_tracer_minimum_step
    )
    stream_tracer_source.InitialStepLength = (
        plot_properties.stream_tracer_initial_step
    )
    stream_tracer_source.MaximumStepLength = (
        plot_properties.stream_tracer_maximum_step
    )

    stream_tracer_source.UpdatePipeline()

    return stream_tracer_source
