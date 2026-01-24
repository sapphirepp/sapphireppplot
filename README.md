![logo](/docs/_static/logo.png)

# Sapphire++ — Plot

A [ParaView](https://www.paraview.org/)
[Python](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
package to plot the results from
[Sapphire++](https://sapphirepp.org/).

It is highly recommended to first familiarize yourself with
the [ParaView](https://www.paraview.org/) GUI,
for example using the
[Sapphire++ ParaView Tutorial](https://sapphirepp.org/latest/paraview-tutorial.html).

This package is built on top of the
[ParaView Python](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
interface.
It tries to abstract it and provide standard plots,
so the user is not exposed to the (cumbersome) ParaView Python interface.
Nevertheless, you might need to fall back on it for custom options.
An extensive
[ParaView Python Introduction](https://sapphirepp.org/latest/paraview-python.html)
is provided on the Sapphire++ website.

An introduction to Sapphire++ — Plot is given in the
[Quick-start](plot.sapphirepp.org/main/examples/plot_quick_start.html)
and the [Tutorial using Jupyter notebooks](https://plot.sapphirepp.org/main/examples/jupyter_tutorial.html).
More example scripts can be found in the
[Sapphire++ examples](https://github.com/sapphirepp/sapphirepp/tree/main/examples).

> [!CAUTION]
> This package is developed for personal use
> and is therefore not claimed to be generally applicable to all Sapphire++ results
> and might exhibit unexpected behaviours.

## Installation

Installing Python packages for ParaView can be non‑trivial.
We recommend using virtual environments so packages are properly linked to ParaView.
Here we present simplified instructions using Conda,
refer to the [Sapphire++ — Plot Website](https://plot.sapphirepp.org/main/installation.html)
for detailed installation instructions.

As prerequisite, we assume you have a
[Conda](https://docs.conda.io)/[conda-forge](https://conda-forge.org)/[Miniforge](https://github.com/conda-forge/miniforge)
installed.

1. Clone the repository:

   ```shell
   git clone https://github.com/sapphirepp/sapphireppplot.git
   cd sapphireppplot
   ```

2. Create `sapplot` Conda environment and install ParaView and other prerequisites:

   ```shell
   conda env create -f environment.yml
   conda activate sapplot
   ```

3. Install `sapphireppplot` (example developer mode):

   ```shell
   pip install -e '.[dev]'
   ```

After this, scripts should work from the terminal with `python`, `pvpython`, or `pvbatch`,
and inside the ParaView GUI.
To run ParaView using the Conda environment:

```shell
conda activate sapplot
paraview
```