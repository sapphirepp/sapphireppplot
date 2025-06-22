"""Module for MHD specific plotting"""

from dataclasses import dataclass

from sapphireppplot.plot_properties import PlotProperties


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
