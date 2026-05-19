"""Define PlotPropertiesAthena class."""

from dataclasses import dataclass

from sapphireppplot.plot_properties_mhd import PlotPropertiesMHD


@dataclass
class PlotPropertiesAthena(PlotPropertiesMHD):
    """
    Specialized plot properties for Athena plots.
    """

    def __post_init__(self) -> None:
        self.data_type = "CELLS"

        self.series_names = [
            "dens",
            "Etot",
            "mom",
            "dens",
        ]

        quantities = [
            "rho",
            "E",
            "p_x",
            "p_y",
            "p_z",
            "b_x",
            "b_y",
            "b_z",
        ]

        self.quantity_names = {
            "rho": "dens",
            "E": "Etot",
            "p_x": "mom_X",
            "p_y": "mom_Y",
            "p_z": "mom_Z",
            "b_x": "Bcc_X",
            "b_y": "Bcc_Y",
            "b_z": "Bcc_Z",
        }

        for quantity in quantities:
            tmp_quantity_name = self.quantity_name(quantity)
            self.labels[tmp_quantity_name] = self.quantity_label(quantity)
            self.line_styles[tmp_quantity_name] = "1"
            if self.line_colors:
                if (quantity in self.line_colors.keys()) and (
                    tmp_quantity_name not in self.line_colors.keys()
                ):
                    self.line_colors[tmp_quantity_name] = self.line_colors[
                        quantity
                    ]
