# Installation

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

:::{note}
For older ParaView versions,
if you want to use it on a remote server,
you might want to install the
[`egl` version](https://www.paraview.org/paraview-docs/v5.13.3/cxx/Offscreen.html):

```shell
conda install paraview=5.13.3=\*_egl
```

Or manually specify a build version found
[here](https://anaconda.org/conda-forge/paraview/files):

```shell
conda install paraview=5.13.3=pyXXXX_XX_egl
```

This changed with ParaView 6.0.0,
an off-screen version can directly be included in the build.

:::

## Further resources

An alternative installation is to change the `PYTHONPATH`,
see the [ParaView tutorial](https://docs.paraview.org/en/latest/Tutorials/SelfDirectedTutorial/batchPythonScripting.html#starting-the-python-interpreter).
This [blog post](https://mbarzegary.github.io/2022/01/03/use-python-packages-modules-in-paraview/)
presents simplified instructions.

Further reading:

- [Sapphire++ ParaView Python introduction](https://sapphirepp.org/latest/paraview-python.html)
- [`paraview.simple` documentation](https://www.paraview.org/paraview-docs/nightly/python/paraview.servermanager_proxies.html#)