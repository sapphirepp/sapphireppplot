"""Define PlotPropertiesSatanic class."""

from dataclasses import dataclass

from sapphireppplot.plot_properties import PlotProperties


@dataclass
class PlotPropertiesSatanic(PlotProperties):
    """
    Specialized plot properties for SATANIC (Solving Acceleration, Transport And Non-thermal Interactions in star Clusters) plots.
    """

    dimension: int = 2
    """Dimensionality of the results."""

    spectral_rescale: float = 3.0
    """The spectral rescaling ``s`` of distribution function :math:`F = p^s f`."""

    quantity_name: str = "F"
    """Name of quantity to plot."""

    unit_r: str = "pc"
    """Unit for radius :math:`r`."""
    unit_p: str = "GeV/c"
    """Unit for momentum :math:`p`."""
    unit_t: str = "Myr"
    """Unit for time :math:`t`."""

    def __post_init__(self) -> None:
        self.update_properties()

    def update_properties(self) -> None:
        """Update PlotProperties from current values."""
        self.series_names = [self.quantity_name]
        # self.labels[self.quantity_name] = r"$p^s f$"
        self.labels[self.quantity_name] = rf"$p^{self.spectral_rescale:.0f} f$"
        self.grid_labels = (r"$r$ / " + self.unit_r, r"$\ln p$", r"$\mu$")
