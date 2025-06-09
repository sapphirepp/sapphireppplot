"""Module for plotting linear-wave-1d"""

#### import the simple module from the paraview
import sys
import paraview.simple as ps
import paraview.util


def get_results_folder() -> str:
    """
    Prompts the user to specify the path to a results folder.

    If the script from command line with arguments
    it uses the first argument as the results folder path.
    Otherwise, it prompts the user to input the path manually.

    Returns
    -------
    str
        The path to the results folder.
    """
    results_folder = ""
    if len(sys.argv) > 1:
        results_folder = sys.argv[1]
    if not results_folder:
        results_folder = input("Path to results folder: ")
    print(f"Using results in '{results_folder}'")
    return results_folder


def load_solution_pvtu(results_folder: str):
    """
    Loads a series of .pvtu solution files from the specified results folder
    using ParaView's XMLPartitionedUnstructuredGridReader.

    Parameters
    ----------
    results_folder : str
        Path to the folder containing solution_*.pvtu files.

    Returns
    -------
    XMLPartitionedUnstructuredGridReader
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.

    Notes
    -----
    - The 'TimeArray' property is set to "None".
    """
    pvtu_files = paraview.util.Glob(results_folder + "/solution_*.pvtu")
    if not pvtu_files:
        raise FileNotFoundError(
            f"No .pvtu files found matching '{results_folder}/solution_*.pvtu'"
        )

    # create a new 'XML Partitioned Unstructured Grid Reader'
    solution = ps.XMLPartitionedUnstructuredGridReader(
        registrationName="solution",
        FileName=pvtu_files,
    )
    solution.UpdatePipelineInformation()
    # Properties modified on solution
    solution.PointArrayStatus = [
        "numeric_rho",
        "numeric_E",
        "numeric_p",
        "numeric_p_z",
        "numeric_b",
        "numeric_b_y",
        "project_rho",
        "project_E",
        "project_p",
        "project_p_z",
        "project_b",
        "project_b_y",
    ]
    solution.TimeArray = "None"
    return solution


def load_solution_vtu(results_folder: str):
    """
    Loads a series of .vtu solution files from the specified results folder
    using ParaView's XMLUnstructuredGridReader.

    Parameters
    ----------
    results_folder : str
        Path to the folder containing solution_*.pvtu files.

    Returns
    -------
    XMLUnstructuredGridReader
        A ParaView reader object with selected point arrays enabled.

    Raises
    ------
    FileNotFoundError
        If no .pvtu files are found in the `results_folder`.
    """
    vtu_files = paraview.util.Glob(results_folder + "/solution_*.vtu")
    if not vtu_files:
        raise FileNotFoundError(
            f"No .pvtu files found matching '{results_folder}/solution_*.vtu'"
        )

    # create a new 'XML Unstructured Grid Reader'

    solution = ps.XMLUnstructuredGridReader(
        registrationName="solution",
        FileName=vtu_files,
    )
    solution.UpdatePipelineInformation()
    # Properties modified on solution
    solution.PointArrayStatus = [
        "numeric_rho",
        "numeric_E",
        "numeric_p",
        "numeric_p_z",
        "numeric_b",
        "numeric_b_y",
        "project_rho",
        "project_E",
        "project_p",
        "project_p_z",
        "project_b",
        "project_b_y",
    ]
    solution.TimeArray = "TIME"
    return solution


def set_display_properties(solution_display):
    """
    Configures the display properties for solution_display,
    like labels, colors, and line styles.

    Parameters
    ----------
    solution_display
    """
    solution_display.SeriesLabel = [
        "numeric_rho",
        "$\\rho$",
        "numeric_E",
        "$E$",
        "numeric_p_X",
        "$p_x$",
        "numeric_p_z",
        "$p_z$",
        "numeric_b_X",
        "$B_x$",
        "numeric_b_y",
        "$B_y$",
        "project_rho",
        "$\\rho_{ana}$",
        "project_E",
        "$E_{ana}$",
        "project_p_X",
        "$p_{x,ana}$",
        "project_p_z",
        "$p_{z,ana}$",
        "project_b_X",
        "$B_{x,ana}$",
        "project_b_y",
        "$B_{y,ana}$",
    ]
    solution_display.SeriesColor = [
        "numeric_rho",
        "0.3000076413154602",
        "0.6899977326393127",
        "0.2899976968765259",
        "numeric_E",
        "0.22000457346439362",
        "0.4899977147579193",
        "0.7199969291687012",
        "numeric_p_X",
        "0.6000000238418579",
        "0.31000229716300964",
        "0.6399939060211182",
        "numeric_p_z",
        "0.22000457346439362",
        "0.4899977147579193",
        "0.7199969291687012",
        "numeric_b_X",
        "0.3000076413154602",
        "0.6899977326393127",
        "0.2899976968765259",
        "numeric_b_y",
        "0",
        "0",
        "0",
        "project_rho",
        "0.3000076413154602",
        "0.6899977326393127",
        "0.2899976968765259",
        "project_E",
        "0.22000457346439362",
        "0.4899977147579193",
        "0.7199969291687012",
        "project_p_X",
        "0.6000000238418579",
        "0.31000229716300964",
        "0.6399939060211182",
        "project_p_z",
        "0.22000457346439362",
        "0.4899977147579193",
        "0.7199969291687012",
        "project_b_X",
        "0.3000076413154602",
        "0.6899977326393127",
        "0.2899976968765259",
        "project_b_y",
        "0",
        "0",
        "0",
    ]
    solution_display.SeriesLineStyle = [
        "numeric_rho",
        "1",
        "numeric_E",
        "1",
        "numeric_p_X",
        "1",
        "numeric_p_z",
        "1",
        "numeric_b_X",
        "1",
        "numeric_b_y",
        "1",
        "project_rho",
        "2",
        "project_E",
        "2",
        "project_p_X",
        "2",
        "project_p_z",
        "2",
        "project_b_X",
        "2",
        "project_b_y",
        "2",
    ]


def plot_line_chart_view(
    solution,
    layout_name: str = "Layout #1",
    title: str = "",
    visible_lines: list[str] = None,
):
    """
    Creates and configures a line chart view
    for visualizing data from a given solution in ParaView.

    Parameters
    ----------
    solution
        The data source to visualize, typically a ParaView data object.
    layout_name : str, optional
        Name of the layout to create for the chart.
    title : str, optional
        Title for the left axis of the chart.
    visible_lines : list[str], optional
        List of series names to display in the chart.

    Returns
    -------
    layout : paraview.servermanager.LayoutProxy
        The layout object containing the configured chart view.
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """

    # create new layout object 'Layout #1'
    layout = ps.CreateLayout(name=layout_name)

    # Create a new 'Line Chart View'
    line_chart_view = ps.CreateView("XYChartView")
    line_chart_view.BottomAxisTitle = "$x$"
    line_chart_view.LeftAxisTitle = title
    line_chart_view.ChartTitleFontSize = 30
    line_chart_view.LeftAxisTitleFontSize = 24
    line_chart_view.BottomAxisTitleFontSize = 24
    line_chart_view.LegendFontSize = 18
    line_chart_view.LeftAxisLabelFontSize = 18
    line_chart_view.BottomAxisLabelFontSize = 18

    # assign view to a particular cell in the layout
    ps.AssignViewToLayout(view=line_chart_view, layout=layout, hint=0)

    # set active source
    ps.SetActiveSource(solution)

    # show data in view
    solution_display = ps.Show(
        solution, line_chart_view, "XYChartRepresentation"
    )
    # Enter preview mode
    layout.PreviewMode = [1280, 720]
    # layout/tab size in pixels
    layout.SetSize(1280, 720)

    # Properties modified on solution_display
    solution_display.UseIndexForXAxis = 0
    solution_display.XArrayName = "Points_X"
    set_display_properties(solution_display)
    solution_display.SeriesVisibility = visible_lines

    return layout, line_chart_view


def save_screenshot(line_chart_view, results_folder: str, filename: str):
    """
    Saves a screenshot of the given line chart view as 'png'.

    Parameters
    ----------
    line_chart_view
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    print(f"Save screenshot '{results_folder}/{filename}.png'")
    ps.SaveScreenshot(
        filename=results_folder + "/" + filename + ".png",
        viewOrLayout=line_chart_view,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=1,
    )


def save_animation(line_chart_view, results_folder: str, filename: str):
    """
    Saves an animation of the given line chart view as series of 'png'.

    Parameters
    ----------
    line_chart_view
        The ParaView view or layout object to capture in the screenshot.
    results_folder : str
        The directory path where the screenshot will be saved.
    filename : str
        The base name for the screenshot file (without extension).
    """
    print(f"Save animation '{results_folder}/{filename}.*.png'")
    ps.SaveAnimation(
        filename=results_folder + "/" + filename + ".png",
        viewOrLayout=line_chart_view,
        location=ps.vtkPVSession.DATA_SERVER,
        TransparentBackground=1,
        FrameStride=1,
    )


def plot_quantity(
    solution,
    results_folder: str,
    quantity: str,
    do_save_animation=False,
):
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution.


    Parameters
    ----------
    solution
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantity : str
        The physical quantity to plot.
        Supported values are:
            - "rho" (density)
            - "E" (energy).
    do_save_animation : bool, optional
        If True, also saves an animation of the plot.
        Defaults to False.

    Returns
    -------
    layout
        The layout object used for the plot.

    Raises
    ------
    ValueError
        If an unsupported quantity is specified.
    """
    filename = "linear-wave-1d-" + quantity
    layout_name = "Layout " + quantity
    title = ""
    visible_lines = None

    if quantity == "rho":
        title = "$\\rho$"
        visible_lines = ["numeric_rho", "project_rho"]
    elif quantity == "E":
        title = "$E$"
        visible_lines = ["numeric_E", "project_E"]
    elif quantity == "p_z":
        title = "$p_z$"
        visible_lines = ["numeric_p_z", "project_p_z"]
    elif quantity == "b_x":
        title = "$B_x$"
        visible_lines = ["numeric_b_X", "project_b_X"]
    elif quantity == "b_y":
        title = "$B_y$"
        visible_lines = ["numeric_b_y", "project_b_y"]
    else:
        raise ValueError(f"Unknown quantity: '{quantity}'")

    layout, line_chart_view = plot_line_chart_view(
        solution, layout_name, title, visible_lines
    )

    save_screenshot(line_chart_view, results_folder, filename)
    if do_save_animation:
        save_animation(line_chart_view, results_folder, filename)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout
