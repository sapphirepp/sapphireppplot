"""Module for MHD specific plotting"""

from dataclasses import dataclass
from typing import Optional
import copy
import paraview.simple as ps
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
    annotation_project_interpol : str
        Label annotation for projected/interpolated solution.
    show_indicators : bool
        Show debug indicators, like the shock indicator.
    """

    dimension: int = 3
    prefix_numeric: bool = False
    project: bool = False
    interpol: bool = False
    annotation_project_interpol: str = "ana"
    show_indicators: bool = False

    def __post_init__(self):
        self.series_names = []
        self.labels = {}
        self.colors = {}
        self.line_styles = {}

        quantities = [
            "rho",
            "E",
            "p_x",
            "p_y",
            "p_z",
            "b_x",
            "b_y",
            "b_z",
            "P",
            "u_x",
            "u_y",
            "u_z",
            "psi",
        ]

        prefix_list = [""]
        label_postfix_list = [""]
        line_style_list = ["1"]
        if self.prefix_numeric:
            prefix_list = ["numeric_"]
        if self.project:
            prefix_list += ["project_"]
            label_postfix_list += [self.annotation_project_interpol]
            line_style_list += ["2"]
        if self.interpol:
            prefix_list += ["interpol_"]
            label_postfix_list += [self.annotation_project_interpol]
            line_style_list += ["2"]

        for i, prefix in enumerate(prefix_list):
            label_postfix = label_postfix_list[i]
            line_style = line_style_list[i]

            self.series_names += [
                prefix + "rho",
                prefix + "E",
                prefix + "p",
                prefix + "b",
                prefix + "P",
                prefix + "u",
                prefix + "psi",
            ]
            if self.dimension <= 1:
                self.series_names += [
                    prefix + "p_y",
                    prefix + "b_y",
                    prefix + "u_y",
                ]
            if self.dimension <= 2:
                self.series_names += [
                    prefix + "p_z",
                    prefix + "b_z",
                    prefix + "u_z",
                ]

            for quantity in quantities:
                self.labels[self.quantity_name(quantity, prefix)] = (
                    self.quantity_label(quantity, label_postfix)
                )
                self.line_styles[self.quantity_name(quantity, prefix)] = (
                    line_style
                )

            new_colors = {
                self.quantity_name("rho", prefix): [
                    "0.3000076413154602",
                    "0.6899977326393127",
                    "0.2899976968765259",
                ],
                self.quantity_name("E", prefix): [
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                ],
                self.quantity_name("p_x", prefix): [
                    "0.6000000238418579",
                    "0.31000229716300964",
                    "0.6399939060211182",
                ],
                self.quantity_name("p_y", prefix): ["0", "0", "0"],
                self.quantity_name("p_z", prefix): [
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                ],
                self.quantity_name("b_x", prefix): [
                    "0.3000076413154602",
                    "0.6899977326393127",
                    "0.2899976968765259",
                ],
                self.quantity_name("b_y", prefix): ["0", "0", "0"],
                self.quantity_name("b_z", prefix): ["0", "0", "0"],
                self.quantity_name("P", prefix): [
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                ],
                self.quantity_name("u_x", prefix): [
                    "0.6000000238418579",
                    "0.31000229716300964",
                    "0.6399939060211182",
                ],
                self.quantity_name("u_y", prefix): ["0", "0", "0"],
                self.quantity_name("u_z", prefix): [
                    "0.22000457346439362",
                    "0.4899977147579193",
                    "0.7199969291687012",
                ],
                self.quantity_name("psi", prefix): ["0", "0", "0"],
            }
            self.line_colors.update(new_colors)

        if self.show_indicators:
            indicators = [
                "magnetic_divergence",
                "shock_indicator",
                "positivity_limiter",
                "subdomian",
            ]
            self.series_names += indicators
            for quantity in indicators:
                self.labels[self.quantity_name(quantity)] = self.quantity_label(
                    quantity
                )
                self.line_styles[self.quantity_name(quantity)] = "1"

            new_colors = {
                "magnetic_divergence": [
                    "0.3000076413154602",
                    "0.6899977326393127",
                    "0.2899976968765259",
                ],
                "shock_indicator": [
                    "0.6500037908554077",
                    "0.34000152349472046",
                    "0.1600061058998108",
                ],
                "positivity_limiter": ["0", "0", "0"],
                "subdomian": ["0", "0", "0"],
            }
            self.line_colors.update(new_colors)

    def quantity_name(self, quantity: str, prefix: str = "") -> str:
        """
        Look up of ParaView series names for quantities.

        Parameters
        ----------
        quantity : str
            The physical quantity.
        prefix : str, optional
            Prefix

        Returns
        -------
        quantity_name : str
            The ParaView Series name for the quantity.
        """
        indicators = [
            "magnetic_divergence",
            "shock_indicator",
            "positivity_limiter",
            "subdomian",
        ]
        if quantity in indicators:
            return quantity

        quantity_names = {
            "rho": "rho",
            "E": "E",
            "p_x": "p_X",
            "p_y": "p_Y",
            "p_z": "p_Z",
            "b_x": "b_X",
            "b_y": "b_Y",
            "b_z": "b_Z",
            "P": "P",
            "u_x": "u_X",
            "u_y": "u_Y",
            "u_z": "u_Z",
            "psi": "psi",
        }
        if self.dimension <= 1:
            quantity_names["p_y"] = "p_y"
            quantity_names["b_y"] = "b_y"
            quantity_names["u_y"] = "u_y"
        if self.dimension <= 2:
            quantity_names["p_z"] = "p_z"
            quantity_names["b_z"] = "b_z"
            quantity_names["u_z"] = "u_z"

        return prefix + quantity_names[quantity]

    def quantity_label(self, quantity: str, annotation: str = "") -> str:
        """
        Look up of label for quantities.

        Parameters
        ----------
        quantity : str
            The physical quantity.
        annotation : str, optional
            Postfix annotation of quantity.

        Returns
        -------
        quantity_label : str
            The label for the quantity.
        """
        tmp_postfix_1 = ""
        tmp_postfix_2 = ""
        if annotation:
            tmp_postfix_1 = r"_{" + annotation + r"}"
            tmp_postfix_2 = ", " + annotation
        quantity_labels = {
            "rho": r"$\rho" + tmp_postfix_1 + r"$",
            "E": r"$E" + tmp_postfix_1 + r"$",
            "p_x": r"$p_{x" + tmp_postfix_2 + r"}$",
            "p_y": r"$p_{y" + tmp_postfix_2 + r"}$",
            "p_z": r"$p_{z" + tmp_postfix_2 + r"}$",
            "b_x": r"$B_{x" + tmp_postfix_2 + r"}$",
            "b_y": r"$B_{y" + tmp_postfix_2 + r"}$",
            "b_z": r"$B_{z" + tmp_postfix_2 + r"}$",
            "P": r"$P" + tmp_postfix_1 + r"$",
            "u_x": r"$_{x" + tmp_postfix_2 + r"}$",
            "u_y": r"$_{y" + tmp_postfix_2 + r"}$",
            "u_z": r"$_{z" + tmp_postfix_2 + r"}$",
            "psi": r"$\psi" + tmp_postfix_1 + "r$",
            "magnetic_divergence": r"$\nabla \cdot \mathbf{B}$",
            "shock_indicator": "Shock Indicator",
            "positivity_limiter": "Pos. Limiter",
            "subdomian": "Subdomain",
        }

        return quantity_labels[quantity]


def plot_quantities_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties: PlotPropertiesMHD,
    value_range: Optional[list[float]] = None,
    do_save_animation=False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 1D.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantities : list[str]
        List of physical quantity to plot.
    name : str
        Name of the layout and image/animation files.
    plot_properties : plot_properties, optional
        Properties for plotting.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    do_save_animation : bool, optional
        If True, also saves an animation of the plot.
        Defaults to False.

    Returns
    -------
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    line_chart_view : paraview.servermanager.XYChartViewProxy
        The configured XY chart view.
    """
    title = r"$\mathbf{w}(x)$"
    if len(quantities) == 1:
        title = plot_properties.quantity_label(quantities[0])

    visible_lines = []
    for quantity in quantities:
        if plot_properties.prefix_numeric:
            visible_lines += [
                plot_properties.quantity_name(quantity, "numeric_")
            ]
        else:
            visible_lines += [plot_properties.quantity_name(quantity)]
        if plot_properties.project:
            visible_lines += [
                plot_properties.quantity_name(quantity, "project_")
            ]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.quantity_name(quantity, "interpol_")
            ]

    # create new layout object
    layout = ps.CreateLayout(name)
    line_chart_view = plot.plot_line_chart_view(
        solution,
        layout,
        title=title,
        visible_lines=visible_lines,
        value_range=value_range,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, name)
    if do_save_animation:
        plot.save_animation(layout, results_folder, name)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout, line_chart_view


def plot_split_view_1d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantities: list[str],
    name: str,
    plot_properties_in: PlotPropertiesMHD,
    labels: Optional[list[str]] = None,
    value_range: Optional[list[float]] = None,
    do_save_animation=False,
) -> paraview.servermanager.ViewLayoutProxy:
    """
    Creates a split plot of with one quantity per line chart plot.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantities : list[str]
        List of physical quantity to plot.
    name : str
        Name of the layout and image/animation files.
    plot_properties : plot_properties, optional
        Properties for plotting.
    labels : Optional[list[str]], optional
        Labels for the numeric and projected/interpolated solution.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    do_save_animation : bool, optional
        If True, also saves an animation of the plot.
        Defaults to False.

    Returns
    -------
    paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    """
    # create new layout object
    layout = ps.CreateLayout(name)

    # split cell
    layout.SplitHorizontal(0, 0.5)
    # layout.SplitVertical(1, 0.5)
    layout.SplitVertical(1, 1.0 / 3.0)
    layout.SplitVertical(4, 0.5)
    # layout.SplitVertical(2, 0.5)
    layout.SplitVertical(2, 1.0 / 3.0)
    layout.SplitVertical(6, 0.5)
    layout.EqualizeViews()

    # Temporarily modify properties
    plot_properties = copy.deepcopy(plot_properties_in)
    # Set all lines black
    for key in plot_properties.line_colors:
        plot_properties.line_colors[key] = ["0", "0", "0"]

    for i, quantity in enumerate(quantities):
        title = plot_properties.quantity_label(quantity)

        visible_lines = []
        if plot_properties.prefix_numeric:
            visible_lines += [
                plot_properties.quantity_name(quantity, "numeric_")
            ]
        else:
            visible_lines += [plot_properties.quantity_name(quantity)]
        if plot_properties.project:
            visible_lines += [
                plot_properties.quantity_name(quantity, "project_")
            ]
        if plot_properties.interpol:
            visible_lines += [
                plot_properties.quantity_name(quantity, "interpol_")
            ]
        if labels:
            plot_properties.labels = {
                plot_properties.quantity_name(quantity, "numeric_"): labels[0],
                plot_properties.quantity_name(quantity, "project_"): labels[1],
                plot_properties.quantity_name(quantity, "interpol_"): labels[1],
            }

        # The subplots seem to work without the `hint` parameter?!
        line_chart_view = plot.plot_line_chart_view(
            solution,
            layout,
            title=title,
            visible_lines=visible_lines,
            value_range=value_range,
            plot_properties=plot_properties,
        )
        line_chart_view.ShowLegend = 0
        if i == 0 and labels:
            line_chart_view.ShowLegend = 1

    plot.save_screenshot(layout, results_folder, name)
    if do_save_animation:
        plot.save_animation(layout, results_folder, name)

    return layout


def plot_quantity_2d(
    solution: paraview.servermanager.SourceProxy,
    results_folder: str,
    quantity: str,
    name: str,
    plot_properties: PlotPropertiesMHD,
    value_range: Optional[list[float]] = None,
    do_save_animation=False,
) -> tuple[
    paraview.servermanager.ViewLayoutProxy, paraview.servermanager.Proxy
]:
    """
    Plots and saves a visualization of a specified physical quantity
    from the solution in 2D.

    Parameters
    ----------
    solution : paraview.servermanager.SourceProxy
        The simulation or computation result containing the data to plot.
    results_folder : str
        Path to the folder where results (images/animations) will be saved.
    quantity : str
        The physical quantity to plot.
    plot_properties : plot_properties, optional
        Properties for plotting.
    value_range : list[float], optional
        Minimal (`value_range[0]`)
        and maximal (`value_range[1]`) value for the y-axes.
    do_save_animation : bool, optional
        If True, also saves an animation of the plot.
        Defaults to False.

    Returns
    -------
    layout : paraview.servermanager.ViewLayoutProxy
        The layout object used for the plot.
    render_view : paraview.servermanager.RenderViewProxy
        The configured 2D render view.
    """

    legend_title = plot_properties.quantity_label(quantity)

    # create new layout object
    layout = ps.CreateLayout(name)
    render_view = plot.plot_render_view_2d(
        solution,
        layout,
        plot_properties.quantity_name(quantity),
        legend_title=legend_title,
        value_range=value_range,
        plot_properties=plot_properties,
    )

    plot.save_screenshot(layout, results_folder, name)
    if do_save_animation:
        plot.save_animation(layout, results_folder, name)

    # Exit preview mode
    # layout.PreviewMode = [0, 0]
    return layout, render_view
