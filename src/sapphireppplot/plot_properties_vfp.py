"""Module for VFP specific plotting"""

from dataclasses import dataclass

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
    _dim_ps : int
        Dimension of the reduced phase space.
    _dim_cs : int
        Spatial dimension of the results.
    momentum : bool
        Does the solution have a momentum dependence?
    expansion_order : int
        Expansion order l_max of the solution.

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
    _dim_ps: int = 2
    _dim_cs: int = 1
    logarithmic_p: bool = True
    expansion_order: int = 1

    prefix_numeric: bool = False
    project: bool = False
    interpol: bool = False
    annotation_project_interpol: str = "ana"

    def __post_init__(self):
        self._dim_ps = self.dimension
        self._dim_cs = self.dimension - self.momentum

        if self.momentum:
            if self.logarithmic_p:
                self.grid_labels[self._dim_ps - 1] = r"$\ln p$"
            else:
                self.grid_labels[self._dim_ps - 1] = r"$p$"

        lms_indices = self.create_lms_indices(self.expansion_order)

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

    def create_lms_indices(self, expansion_order: int) -> list[list[int]]:
        """
        Create a mapping between the system index $i$ and the
        spherical harmonic indices $(l,m,s)$.

        Parameters
        ----------
        expansion_order : int
            Expansion order l_max of the solution.

        Returns
        -------
        lms_indices : list[list[int]]
            Mapping `lms_indices[i] = [l,m,s]`.
        """
        system_size = (expansion_order + 1) ** 2
        lms_indices = []

        l = 0
        m = 0
        for _ in range(system_size):
            s = 0 if m <= 0 else 1
            lms_indices += [[l, abs(m), s]]

            m += 1
            if m > l:
                l += 1
                m = -l
        return lms_indices

    def f_lms_name(self, lms_index: list[int], prefix: str = "") -> str:
        """
        Look up of ParaView series names for specific lms_index.

        Parameters
        ----------
        lms_index : list[int]
            The index `[l,m,s]`.
        prefix : str, optional
            Prefix.

        Returns
        -------
        quantity_name : str
            The ParaView Series name for the lms_index.
        """
        return prefix + f"f_{lms_index[0]}{lms_index[1]}{lms_index[2]}"

    def f_lms_label(self, lms_index: list[int], annotation: str = "") -> str:
        """
        Look up of label for lms_index.

        Parameters
        ----------
        lms_index : list[int]
            The index `[l,m,s]`.
        annotation : str, optional
            Postfix annotation of quantity.

        Returns
        -------
        quantity_label : str
            The label for the lms_index.
        """
        tmp_postfix = ""
        if annotation:
            tmp_postfix = " ," + annotation

        return f"$f_{{ {lms_index[0]} {lms_index[1]} {lms_index[2]} {tmp_postfix} }}$"
