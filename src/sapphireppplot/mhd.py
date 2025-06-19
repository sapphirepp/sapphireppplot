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
    dimension : int
        Dimensionality of the results.
    prefix_numeric : bool
        Use numeric prefix for results.
    project : bool
        Show projected solution.
    interpol : bool
        Show interpolated solution.
    """

    dimension: int = 1
    prefix_numeric: bool = False
    project: bool = False
    interpol: bool = False

    def __post_init__(self):
        self.series_names = []
        self.labels = []
        self.colors = []
        self.line_styles = []

        prefix_list = [""]
        label_postfix_list = [""]
        line_style_list = ["1"]
        if self.prefix_numeric:
            prefix_list = ["numeric_"]
        if self.project:
            prefix_list += ["project_"]
            label_postfix_list += ["ana"]
            label_postfix_list += ["2"]
        if self.interpol:
            prefix_list += ["interpol_"]
            label_postfix_list += ["ana"]
            label_postfix_list += ["2"]

        for i, prefix in enumerate(prefix_list):
            label_postfix = label_postfix_list[i]
            line_style = line_style_list[i]

            self.series_names += [
                prefix + "rho",
                prefix + "E",
                prefix + "p",
                prefix + "b",
            ]
            self.colors += [
                prefix + "rho",
                "0.3000076413154602",
                "0.6899977326393127",
                "0.2899976968765259",
                prefix + "E",
                "0.22000457346439362",
                "0.4899977147579193",
                "0.7199969291687012",
                prefix + "p_X",
                "0.6000000238418579",
                "0.31000229716300964",
                "0.6399939060211182",
                prefix + "b_X",
                "0.3000076413154602",
                "0.6899977326393127",
                "0.2899976968765259",
            ]
            self.line_styles += [
                prefix + "rho",
                line_style,
                prefix + "E",
                line_style,
                prefix + "p_X",
                line_style,
                prefix + "b_X",
                line_style,
            ]

            if self.dimension <= 1:
                self.series_names += [
                    prefix + "p_y",
                    prefix + "b_y",
                ]
                self.colors += [
                    prefix + "p_y",
                    "0",
                    "0",
                    "0",
                    prefix + "b_y",
                    "0",
                    "0",
                    "0",
                ]
                self.line_styles += [
                    prefix + "p_y",
                    line_style,
                    prefix + "b_y",
                    line_style,
                ]
            else:
                self.colors += [
                    prefix + "p_Y",
                    "0",
                    "0",
                    "0",
                    prefix + "b_Y",
                    "0",
                    "0",
                    "0",
                ]
                self.line_styles += [
                    prefix + "p_Y",
                    line_style,
                    prefix + "b_Y",
                    line_style,
                ]

            if self.dimension <= 2:
                self.series_names += [
                    prefix + "p_z",
                    prefix + "b_z",
                ]
                self.colors += [
                    prefix + "p_z",
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                    prefix + "b_z",
                    "0",
                    "0",
                    "0",
                ]
                self.line_styles += [
                    prefix + "p_z",
                    line_style,
                    prefix + "b_z",
                    line_style,
                ]
            else:
                self.colors += [
                    prefix + "p_Z",
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                    prefix + "b_Z",
                    "0",
                    "0",
                    "0",
                ]
                self.line_styles += [
                    prefix + "p_",
                    line_style,
                    prefix + "b_",
                    line_style,
                ]

            tmp_postfix_1 = ""
            tmp_postfix_2 = ""
            if label_postfix:
                tmp_postfix_1 = r"_{" + label_postfix + r"}"
                tmp_postfix_2 = ", " + label_postfix
            self.labels += [
                prefix + "rho",
                r"$\rho" + tmp_postfix_1 + r"$",
                prefix + "E",
                r"$E" + tmp_postfix_1 + r"$",
                prefix + "p_X",
                r"$p_{x" + tmp_postfix_2 + r"}$",
                prefix + "B_X",
                r"$B_{x" + tmp_postfix_2 + r"}$",
            ]
            if self.dimension <= 1:
                self.labels += [
                    prefix + "p_y",
                    r"$p_{y" + tmp_postfix_2 + r"}$",
                    prefix + "b_y",
                    r"$B_{y" + tmp_postfix_2 + r"}$",
                ]
            else:
                self.labels += [
                    prefix + "p_Y",
                    r"$p_{y" + tmp_postfix_2 + r"}$",
                    prefix + "b_Y",
                    r"$B_{y" + tmp_postfix_2 + r"}$",
                ]
            if self.dimension <= 2:
                self.labels += [
                    prefix + "p_z",
                    r"$p_{z" + tmp_postfix_2 + r"}$",
                    prefix + "b_z",
                    r"$B_{z" + tmp_postfix_2 + r"}$",
                ]
            else:
                self.labels += [
                    prefix + "p_Z",
                    r"$p_{z" + tmp_postfix_2 + r"}$",
                    prefix + "b_Z",
                    r"$B_{z" + tmp_postfix_2 + r"}$",
                ]

        print(self)


def plot_quantity_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    plot_properties: PlotPropertiesMHD,
    do_save_animation=False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 1D.

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


def plot_quantity_2d(
    solution: paraview.servermanager.SourceProxy,
    animation_scene: paraview.servermanager.Proxy,
    results_folder: str,
    quantity: str,
    plot_properties: PlotPropertiesMHD,
    do_save_animation=False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 2D.

    Parameters
    ----------
    solution: : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantity : str
        The physical quantity to plot.
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

    filename = "blast-wave-" + quantity
    layout_name = "2D Plot " + quantity
    legend_title = ""

    match quantity:
        case "rho":
            legend_title = "$\\rho$"
        case "E":
            legend_title = "$E$"
        case _:
            raise ValueError(f"Unknown quantity: '{quantity}'")

    layout, render_view = plot.plot_render_view_2d(
        solution,
        quantity,
        layout_name=layout_name,
        legend_title=legend_title,
        value_range=[0.08 / 2.0, 6.5 / 2.0],
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, filename)
    animation_scene.AnimationTime = 0.2
    plot.save_screenshot(layout, results_folder, filename + "-t02")
    if do_save_animation:
        plot.save_animation(layout, results_folder, filename)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout
