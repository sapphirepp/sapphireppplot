"""Transform the solution, e.g. by PlotOverLine or Calculator."""

from typing import Optional
import os
import paraview.simple as ps
import paraview.servermanager
from sapphireppplot.plot_properties import PlotProperties

_epsilon_d: float = 1e-10


def plot_over_line(
    solution: paraview.servermanager.SourceProxy,
    direction: str | list[list[float]] = "x",
    offset: Optional[list[float]] = None,
    x_axes_scale: Optional[float] = None,
    results_folder: str = "",
    filename: Optional[str] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Create and configure plot over line from solution.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source.
    direction : str | list[list[float]]
        Direction of the line.
        Either "x", "y", "z", "d" or a list with start and end points.
    offset : list[float], optional
        Offset of the line.
    x_axes_scale : float, optional
        Divide the x-axes coordinate by this scale.
        The scaled axes will be stored in a variable `scaled_axes`.
    results_folder : str
        The directory path where the data will be saved as `.csv`.
    filename : str
        The base name for the saved data file (without extension).
        If no filename is given, the data is not saved.
    plot_properties : PlotProperties, optional
        Properties of the solution, like the sampling pattern.

    Returns
    -------
    plot_over_line_source : paraview.servermanager.SourceProxy
        The PlotOverLine source.
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
            # Extract min_x and max_x from the solution_bounds
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]

            # Properties modified on plot_over_line_source
            plot_over_line_source.Point1 = [min_x, offset[1], offset[2]]
            plot_over_line_source.Point2 = [max_x, offset[1], offset[2]]
        case "y":
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            plot_over_line_source.Point1 = [offset[0], min_y, offset[2]]
            plot_over_line_source.Point2 = [offset[0], max_y, offset[2]]
        case "z":
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
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
                f"Unknown sampling pattern {plot_properties.sampling_pattern}"
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
            location=ps.vtkPVSession.DATA_SERVER,
            ChooseArraysToWrite=(
                1 if plot_properties.series_names is not None else 0
            ),
            PointDataArrays=series_names,
            Precision=5,
            UseScientificNotation=1,
        )

    plot_over_line_source.UpdatePipeline()

    return plot_over_line_source


def clip_area(
    solution: paraview.servermanager.SourceProxy,
    min_x: float = -10,
    max_x: float = 10,
    plot_properties: PlotProperties = PlotProperties(),  # noqa: U100
) -> paraview.servermanager.SourceProxy:
    """
    Clip area from solution.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source.
    min_x : float, optional
        Start clip at min_x,
    min_x : float, optional
        End clip at max_x.
    plot_properties : PlotProperties, optional
        Properties of the solution, like the sampling pattern.

    Returns
    -------
    clipped_solution : paraview.servermanager.SourceProxy
        The clipped source.
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
    n_lines: int = 30,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Create stream tracer of a quantity from the solution.

    The `stream_tracer` can be added to an existing `render_view`
    using `pvplot.show_stream_tracer()`.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source.
    quantity : str
        Name of the quantity for the stream tracer.
    direction : str | list[list[float]]
        Direction of the line.
        Either "x", "y", "z", "d" or a list with start and end points.
    offset : list[float], optional
        Offset of the line.
    n_lines : int, optional
        Number of stream lines.
    plot_properties : PlotProperties, optional
        Properties of the solution.

    Returns
    -------
    paraview.servermanager.SourceProxy
    stream_tracer_source : paraview.servermanager.SourceProxy
        The StreamTracer source.
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
            # Extract min_x and max_x from the solution_bounds
            min_x = solution_bounds[0]
            max_x = solution_bounds[1]

            # Properties modified on stream_tracer_source
            stream_tracer_source.SeedType.Point1 = [min_x, offset[1], offset[2]]
            stream_tracer_source.SeedType.Point2 = [max_x, offset[1], offset[2]]
        case "y":
            min_y = solution_bounds[2]
            max_y = solution_bounds[3]
            stream_tracer_source.SeedType.Point1 = [offset[0], min_y, offset[2]]
            stream_tracer_source.SeedType.Point2 = [offset[0], max_y, offset[2]]
        case "z":
            min_z = solution_bounds[4]
            max_z = solution_bounds[5]
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
