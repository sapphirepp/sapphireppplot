"""Define PlotPropertiesSatanic class."""

from dataclasses import dataclass, field

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

    grid_labels: tuple[str, str, str] = field(
        default_factory=lambda: (r"$r$", r"$\ln p$", r"$\mu$")
    )

    def __post_init__(self) -> None:
        self.series_names = [self.quantity_name]
        self.labels[self.quantity_name] = r"$p^s f$"
