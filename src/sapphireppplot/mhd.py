"""Module for MHD specific plotting"""

from dataclasses import dataclass
import paraview.servermanager

from sapphireppplot.plot_properties import PlotProperties
from sapphireppplot import plot


@dataclass
class PlotPropertiesMHD(PlotProperties):
    """
    Specialized plot properties for MHD plots.

    Attributes
    ----------
    project : bool
        Show projected solution.
    interpol : bool
        Show interpolated solution.
    """

    project: bool = False
    interpol: bool = False

    def __post_init__(self):
        self.series_names = [
            "numeric_rho",
            "numeric_E",
            "numeric_p",
            "numeric_p_z",
            "numeric_b",
            "numeric_b_y",
        ]
        self.labels = [
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
        ]
        self.colors = [
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
        ]
        self.line_styles = [
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
        ]

        if self.project:
            self.series_names += [
                "project_rho",
                "project_E",
                "project_p",
                "project_p_z",
                "project_b",
                "project_b_y",
            ]
            self.labels += [
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
            self.colors += [
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
            self.line_styles += [
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


def plot_quantity_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    plot_properties: PlotPropertiesMHD,
    do_save_animation=False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in !D.

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
    plot_properties : plot_properties, optional
        Properties for plotting.
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
        layout_name=layout_name,
        title=title,
        visible_lines=visible_lines,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, filename)
    if do_save_animation:
        plot.save_animation(layout, results_folder, filename)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout
