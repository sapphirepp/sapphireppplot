"""Module for MHD specific plotting"""

import paraview.servermanager

from sapphireppplot import plot


def get_display_properties() -> tuple[list[str], list[str], list[str]]:
    """
    Configures the display properties for solution_display,
    like labels, colors, and line styles.

    Returns
    -------
    labels : list[str]
        Labels for the quantities.
    colors : list[str]
        Line colors for the quantities.
    line_style : list[str]
        Line styles for the quantities.
    """
    labels = [
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
    colors = [
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
    line_style = [
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

    return labels, colors, line_style


def plot_quantity(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    do_save_animation=False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution.

    Parameters
    ----------
    solution: : paraview.servermanager.SourceProxy
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
    layout : paraview.servermanager.ViewLayoutProxy
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
    labels, colors, line_styles = get_display_properties()

    match quantity:
        case "rho":
            title = "$\\rho$"
            visible_lines = ["numeric_rho", "project_rho"]
        case "E":
            title = "$E$"
            visible_lines = ["numeric_E", "project_E"]
        case "p_z":
            title = "$p_z$"
            visible_lines = ["numeric_p_z", "project_p_z"]
        case "b_x":
            title = "$B_x$"
            visible_lines = ["numeric_b_X", "project_b_X"]
        case "b_y":
            title = "$B_y$"
            visible_lines = ["numeric_b_y", "project_b_y"]
        case _:
            raise ValueError(f"Unknown quantity: '{quantity}'")

    layout, line_chart_view = plot.plot_line_chart_view(
        solution,
        layout_name,
        title,
        visible_lines,
        labels=labels,
        colors=colors,
        line_styles=line_styles,
    )

    plot.save_screenshot(layout, results_folder, filename)
    if do_save_animation:
        plot.save_animation(layout, results_folder, filename)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout
