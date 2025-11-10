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

The installation of Python packages for ParaView is not strait forward.
We refer to the [Sapphire++ Tutorial](https://sapphirepp.org/latest/paraview-python.html)
for an introduction.

This package requires [ParaView](https://www.paraview.org/)
and [paraview.simple](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
to be installed.

We recommanded to install ParaView Python is using
[conda](https://docs.conda.io/)/[conda-forge](https://conda-forge.org/)/[Miniforge](https://github.com/conda-forge/miniforge):

0. Install [Miniforge](https://github.com/conda-forge/miniforge#install):

   If you don't have a `conda` (or similar) installation,
   you can use the following script to install a minimal `conda` version:

   ```shell
   wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh
   ```
  
   Then activate `conda` using:

   ```shell
   source ~/miniforge3/bin/activate
   ```
  
1. Clone the repository:

   ```shell
   git clone https://github.com/sapphirepp/sapphireppplot.git
   cd sapphireppplot
   ```

2. Create `sapplot` conda environment with ParaView and other prerequisites installed:

   ```shell
   conda env create -f environment.yml
   conda activate sapplot
   ```

3. Install `sapphireppplot`:

   ```shell
   pip install -e '.[dev]'
   ```

This ensures that the Python environments are linked correctly,
so the scripts work both from the terminal using
`python`, `pvpython` or `pvbatch`
and inside the ParaView GUI as scripts and macros.

If you want to use the package inside the ParaView GUI,
make sure to use the ParaView installation in the `conda` environment:

```shell
source ~/miniforge3/bin/activate
conda activate sapplot
paraview &
```
