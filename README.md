# Sapphire++ — Plot

A [ParaView](https://www.paraview.org/)
[Python](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
package to plot the results from
[Sapphire++](https://sapphirepp.org/).

This package is developed for personal use
and is therefore claim to be generally applicable to all Sapphire++ results
and might exhibit unexpected behaviours.

## Installation

The installation of Python packages for ParaView is not strait forward.
We refer to the [Sapphire++ Tutorial](https://sapphirepp.org/latest/paraview-python.html)
for an introduction.

This package requires [ParaView](https://www.paraview.org/)
and [pvpython](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
to be installed.

We recommanded to install ParaView Python is using
[conda](https://docs.conda.io/)/[conda-forge](https://conda-forge.org/):

```shell
conda create --name ParaView python=3.13
conda activate ParaView
conda install paraview
```

This ensures that the Python environments are linked correctly,
so the scripts work both from the terminal using
`python`, `pvpython` or `pvbatch`
and inside the ParaView GUI as scripts and macros.

> [!NOTE]
> If you install ParaView on a remote server,
> you might want to install the
> [`egl` version](https://www.paraview.org/paraview-docs/latest/cxx/Offscreen.html).
> To specify the build version use
>
> ```shell
> conda install paraview=5.13.3=pyXXXX_XX_egl
> ```
>
> A list of all builds can be found at the
> [conda webpage](https://anaconda.org/conda-forge/paraview/files).

Now you can install this `sapphireppplot` package using `pip`:

```shell
git clone https://github.com/floschulze/sapphireppplot
pip install -e sapphireppplot
```

If you want to use the package inside the ParaView GUI,
make sure to use the correct ParaView installation that comes with `conda`:

```shell
conda activate ParaView
paraview &
```

## Further resources

An alternative installation is to change the `PYTHONPATH`,
see the [ParaView tutorial](https://docs.paraview.org/en/latest/Tutorials/SelfDirectedTutorial/batchPythonScripting.html#starting-the-python-interpreter).
This [blog post](https://mbarzegary.github.io/2022/01/03/use-python-packages-modules-in-paraview/)
presents simplified instructions.

Further reading:

- [Sapphire++ ParaView Python introduction](https://sapphirepp.org/latest/paraview-python.html)
- [`paraview.simple` documentation](https://www.paraview.org/paraview-docs/nightly/python/paraview.servermanager_proxies.html#)