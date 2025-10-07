"""Define PlotPropertiesVFP class."""

from dataclasses import dataclass, field
from typing import Optional

from sapphireppplot.plot_properties import PlotProperties


@dataclass
class PlotPropertiesVFP(PlotProperties):
    """
    Specialized plot properties for VFP plots.

    Attributes
    ----------
    dimension : int
        Dimensionality of the results.
    momentum : bool
        Does the solution have a momentum dependence?
    dim_ps : int
        Dimension of the reduced phase space.
    dim_cs : int
        Spatial dimension of the results.
    momentum : bool
        Does the solution have a momentum dependence?
    scaled_distribution_function : bool
        Is the distribution function scaled in Sapphire++ as :math:`g = p^s f`?

    lms_indices : list[list[int]], optional
        List of lms_indices to display.
        If left empty it will be set automatically at loading.

    _spectral_index : float, optional
        If set, the distribution function is scaled by this index in ParaView.

    debug_input_functions : bool
        Show user defined input functions.

    prefix_numeric : bool
        Use numeric prefix for results.
    project : bool
        Show projected solution.
    interpol : bool
        Show interpolated solution.
    annotation_project_interpol : str
        Label annotation for projected/interpolated solution.
    """

    dimension: int = 2
    momentum: bool = True
    dim_ps: int = 2
    dim_cs: int = 1
    logarithmic_p: bool = True
    scaled_distribution_function: bool = False

    lms_indices: list[list[int]] = field(default_factory=list)

    debug_input_functions: bool = False

    prefix_numeric: bool = False
    project: bool = False
    interpol: bool = False
    annotation_project_interpol: str = "ana"

    _spectral_index: Optional[float] = None

    def __post_init__(self) -> None:
        self.dim_ps = self.dimension
        self.dim_cs = self.dimension - self.momentum

        if self.momentum:
            if self.logarithmic_p:
                self.grid_labels[self.dim_ps - 1] = r"$\ln p$"
            else:
                self.grid_labels[self.dim_ps - 1] = r"$p$"

        if self.lms_indices:
            self.set_lms_indices(self.lms_indices)

    def _add_debug_input_functions(
        self,
        lms_indices: list[list[int]],
        prefix: str = "func_",
        line_style: str = "1",
    ) -> None:
        """
        Add the debug input functions to plot properties.

        Parameters
        ----------
        lms_indices : list[list[int]]
            The lms_indices to activate for the source.
        prefix : str, optional
            Prefix.
        line_style : str, optional
            Line styles for the series quantities in the LineChartView.
        """
        vec_component_names = ["x", "y", "z"]

        if self.series_names:
            self.series_names += [prefix + "nu"]
        self.labels[prefix + "nu"] = r"$\nu$"
        self.line_styles[prefix + "nu"] = line_style

        for lms_index in lms_indices:
            s_lms_name = self.f_lms_name(lms_index, prefix, base_name="S")
            if self.series_names:
                self.series_names += [s_lms_name]
            self.labels[s_lms_name] = self.f_lms_label(
                lms_index, variable_name="S"
            )
            self.line_styles[s_lms_name] = line_style

        for vec_comp in vec_component_names:
            if self.series_names:
                self.series_names += [prefix + "B_" + vec_comp]
            self.labels[prefix + "B_" + vec_comp] = f"$B_{vec_comp}$"
            self.line_styles[prefix + "B_" + vec_comp] = line_style

        for vec_comp in vec_component_names:
            if self.series_names:
                self.series_names += [prefix + "u_" + vec_comp]
            self.labels[prefix + "u_" + vec_comp] = f"$u_{vec_comp}$"
            self.line_styles[prefix + "u_" + vec_comp] = line_style
        if self.series_names:
            self.series_names += [prefix + "div_u"]
        self.labels[prefix + "div_u"] = r"$\nabla \cdot u$"
        self.line_styles[prefix + "div_u"] = line_style
        for vec_comp in vec_component_names:
            if self.series_names:
                self.series_names += [prefix + "DT_u_" + vec_comp]
            self.labels[prefix + "DT_u_" + vec_comp] = f"$D u_{vec_comp} / Dt$"
            self.line_styles[prefix + "DT_u_" + vec_comp] = line_style
        for vec_comp_i in vec_component_names:
            for vec_comp_j in vec_component_names:
                if self.series_names:
                    self.series_names += [
                        prefix + f"du{vec_comp_i}_d{vec_comp_j}"
                    ]
                self.labels[prefix + f"du{vec_comp_i}_d{vec_comp_j}"] = (
                    f"$d u_{vec_comp_i} / d{vec_comp_j}$"
                )
                self.line_styles[prefix + f"du{vec_comp_i}_d{vec_comp_j}"] = (
                    line_style
                )

    @staticmethod
    def create_lms_indices(expansion_order: int) -> list[list[int]]:
        """
        Create mapping between system index :math:`i` and spherical harmonic indices :math:`(l,m,s)`.

        Parameters
        ----------
        expansion_order : int
            Expansion order `l_max`.

        Returns
        -------
        lms_indices : list[list[int]]
            Mapping `lms_indices[i] = [l,m,s]`.
        """
        system_size = (expansion_order + 1) ** 2
        lms_indices = []

        l = 0  # noqa: E741
        m = 0
        for _ in range(system_size):
            s = 0 if m <= 0 else 1
            lms_indices += [[l, abs(m), s]]

            m += 1
            if m > l:
                l += 1
                m = -l
        return lms_indices

    def f_lms_name(
        self,
        lms_index: list[int],
        prefix: str = "",
        base_name: Optional[str] = None,
    ) -> str:
        """
        Look up of ParaView series names for specific lms_index.

        Parameters
        ----------
        lms_index : list[int]
            The index `[l,m,s]`.
        prefix : str, optional
            Prefix.
        base_name : str, optional
            Base name for variable.
            Defaults to "f", "g" or "p^s f".

        Returns
        -------
        quantity_name : str
            The ParaView Series name for the lms_index.
        """
        if not base_name:
            base_name = "f"
            if self.scaled_distribution_function:
                base_name = "g"
            if self._spectral_index:
                base_name = "p^s f"

        return (
            prefix + f"{base_name}_{lms_index[0]}{lms_index[1]}{lms_index[2]}"
        )

    def f_lms_label(
        self,
        lms_index: list[int] | list[str],
        annotation: str = "",
        variable_name: Optional[str] = None,
    ) -> str:
        """
        Look up of label for lms_index.

        Parameters
        ----------
        lms_index : list[int] | list[str]
            The index `[l,m,s]`.
        annotation : str, optional
            Postfix annotation of quantity.
        variable_name : str, optional
            Name of the variable.
            Defaults to "f", "g" or "p^s f".

        Returns
        -------
        quantity_label : str
            The label for the lms_index.
        """
        if not variable_name:
            variable_name = "f"
            if self.scaled_distribution_function:
                variable_name = "g"
            if self._spectral_index:
                variable_name = f"p^{{ {self._spectral_index:g} }} f"

        tmp_postfix = ""
        if annotation:
            tmp_postfix = " ," + annotation

        return f"${variable_name}_{{ {lms_index[0]} {lms_index[1]} {lms_index[2]} {tmp_postfix} }}$"

    def set_lms_indices(self, lms_indices: list[list[int]]) -> None:
        """
        Set the `series_names` and labels activating only the `lms_indices`.

        Parameters
        ----------
        lms_indices : list[list[int]]
            The lms_indices to activate.
            Will deactivate all other series names.
        """
        self.lms_indices = lms_indices

        self.series_names = []
        self.labels = {}
        # self.colors = {}
        self.line_styles = {}

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

            for lms_index in lms_indices:
                f_lms_name = self.f_lms_name(lms_index, prefix)
                self.series_names += [f_lms_name]
                self.labels[f_lms_name] = self.f_lms_label(
                    lms_index, label_postfix
                )
                self.line_styles[f_lms_name] = line_style

        if self.debug_input_functions:
            self._add_debug_input_functions(lms_indices)

    def set_expansion_order(self, expansion_order: int) -> None:
        """
        Set the `series_names` and labels using the expansion order.

        Parameters
        ----------
        expansion_order : int
            Maximum expansion order `l_max` to display.
        """
        self.set_lms_indices(self.create_lms_indices(expansion_order))

    def scale_by_spectral_index(
        self, spectral_index: float, lms_indices: list[list[int]]
    ) -> None:
        """
        Set properties to a scaled distribution function with spectral index :math:`s`.

        Parameters
        ----------
        spectral_index : float
            Spectral index :math:`s`.
        lms_indices : list[list[int]]
            The lms_indices to activate.
            Will deactivate all other and unscaled series names.
        """
        plot_properties_old = self.copy()
        self._spectral_index = spectral_index

        self.series_names = []

        prefix_list = [""]
        label_postfix_list = [""]
        if self.prefix_numeric:
            prefix_list = ["numeric_"]
        if self.project:
            prefix_list += ["project_"]
            label_postfix_list += [self.annotation_project_interpol]
        if self.interpol:
            prefix_list += ["interpol_"]
            label_postfix_list += [self.annotation_project_interpol]

        for i, prefix in enumerate(prefix_list):
            label_postfix = label_postfix_list[i]

            for lms_index in lms_indices:
                f_lms_name = self.f_lms_name(lms_index, prefix)
                f_lms_name_old = plot_properties_old.f_lms_name(
                    lms_index, prefix
                )
                self.series_names += [f_lms_name]
                self.labels[f_lms_name] = self.f_lms_label(
                    lms_index, label_postfix
                )
                if plot_properties_old.line_styles:
                    self.line_styles[f_lms_name] = (
                        plot_properties_old.line_styles[f_lms_name_old]
                    )
                if plot_properties_old.line_colors:
                    self.line_colors[f_lms_name] = (
                        plot_properties_old.line_colors[f_lms_name_old]
                    )

        if self.debug_input_functions:
            self._add_debug_input_functions(lms_indices)
