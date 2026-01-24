# Installation

Installing Python packages for ParaView can be non‑trivial.
We recommend using virtual environments so packages are properly linked to ParaView.
For this we present two methods:

- [Use Conda to install ParaView](#use-conda-to-install-paraview)
- [Link package to an existing ParaView installation using `venv`](#link-package-to-an-existing-paraview-installation-using-venv)

:::{note}
The ParaView package available via Conda lacks MPI support.
If you need to visualize large simulations,
we recommend linking to an existing ParaView build with MPI support.
:::

## Use Conda to install ParaView

If you do not have [Conda](https://docs.conda.io)/[conda-forge](https://conda-forge.org)/[Miniforge](https://github.com/conda-forge/miniforge),
install Miniforge:

```shell
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Activate Conda (adjust path if you installed Miniforge elsewhere):

```shell
source ~/miniforge3/bin/activate
```

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

## Link package to an existing ParaView installation using `venv`

This assumes you already have [ParaView](https://www.paraview.org)
(and [`pvpython`](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython))
installed.
Install it from the [ParaView download page](https://www.paraview.org/download/) if needed.

The Python version used by the virtual environment must match the Python used by `pvpython`.
Check the version with:

```shell
pvpython -c "import sys; print(sys.executable, sys.version)"
```

1. Create a virtual environment (`venv`):  
   Manually ensure to use a matching Python version!

   ```shell
   python -m venv /path/to/venv/sapplot
   ```

   (Alternatively you can use Conda or `virtualenv`, see above.
   But do not install ParaView in the virtual environment,
   as this can lead to compatibility issues.)

2. Activate the `venv` (note the `/bin/activate`):

   ```shell
   source /path/to/venv/sapplot/bin/activate
   ```

3. Install the package (example from GitHub):

   ```shell
   pip install git+https://github.com/sapphirepp/sapphireppplot.git
   ```

Run scripts with `pvbatch` or start the GUI, pointing ParaView to the `venv`:

```shell
pvbatch --venv=/path/to/venv/sapplot script.py args
paraview --venv=/path/to/venv/sapplot
```
