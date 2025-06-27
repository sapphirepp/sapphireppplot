"""Define PlotPropertiesAthena class"""

from dataclasses import dataclass
from typing import override

from sapphireppplot.mhd import PlotPropertiesMHD


@dataclass
class PlotPropertiesAthena(PlotPropertiesMHD):
    """
    Specialized plot properties for Athena plots.
    """

    def __post_init__(self):
        self.data_type = "CELLS"

        self.series_names = [
            "dens",
            "Etot",
            "mom",
            "dens",
        ]

    @override
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
        quantity_names = {
            "rho": "dens",
            "E": "Etot",
            "p_x": "mom_X",
            "p_y": "mom_Y",
            "p_z": "mom_Z",
            "b_x": "Bcc_X",
            "b_y": "Bcc_Y",
            "b_z": "Bcc_Z",
        }

        if quantity in quantity_names:
            return prefix + quantity_names[quantity]

        if self.series_names and quantity in self.series_names:
            return quantity

        raise ValueError(f"Unknown quantity '{quantity}'!")
