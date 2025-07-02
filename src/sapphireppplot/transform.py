"""Transform the solution, e.g. by PlotOverLine or Calculator"""

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
    results_folder: str = "",
    filename: Optional[str] = None,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Creates and configures a line chart view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The data source.
    direction : str | list[list[float]]
        Direction of the line.
        Either "x", "y", "z", "d" or a list with start and end points.
    offset : list[float], optional
        Offset of the line.
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
    plot_over_line_source = ps.PlotOverLine(registrationName="PlotOverLine",
                                            Input=solution)

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
                plot_over_line_source.Resolution = plot_properties.sampling_resolution
        case "center":
            plot_over_line_source.SamplingPattern = "Sample At Segment Centers"
            if plot_properties.sampling_resolution:
                plot_over_line_source.ComputeTolerance = False
                plot_over_line_source.Tolerance = plot_properties.sampling_resolution
        case "boundary":
            plot_over_line_source.SamplingPattern = "Sample At Cell Boundaries"
            if plot_properties.sampling_resolution:
                plot_over_line_source.ComputeTolerance = False
                plot_over_line_source.Tolerance = plot_properties.sampling_resolution
        case _:
            raise ValueError(
                f"Unknown sampling pattern {plot_properties.sampling_pattern}")

    # Save data if a file is given
    if filename:
        file_path = os.path.join(results_folder, filename + ".csv")
        print(f"Save data '{file_path}'")

        series_names = []
        if plot_properties.series_names:
            series_names += plot_properties.series_names
        if direction == list() or direction == "d":
            series_names += ["arc_length"]

        ps.SaveData(
            filename=file_path,
            proxy=plot_over_line_source,
            location=ps.vtkPVSession.DATA_SERVER,
            ChooseArraysToWrite=(1 if plot_properties.series_names is not None
                                 else 0),
            PointDataArrays=series_names,
            Precision=5,
            UseScientificNotation=1,
        )

    return plot_over_line_source


def clip_area(
    solution: paraview.servermanager.SourceProxy,
    min_x: float = -10,
    max_x: float = 10,
    plot_properties: PlotProperties = PlotProperties(),
) -> paraview.servermanager.SourceProxy:
    """
    Creates and configures a line chart view
    for visualizing data from a given solution in ParaView.

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
        max_x - min_x, max_y - min_y, 2 * _epsilon_d
    ]

    ps.HideInteractiveWidgets(proxy=clipped_solution.ClipType)

    return clipped_solution
