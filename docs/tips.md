# Tips and Tricks

## Preview windows in interactive python shell

When using the interactive python shell,
the plotting scripts may open ParaView preview windows
that can not be interacted with or be closed.
In this case, you can use the
{pv}`paraview.simple.Interact() <paraview.simple.html#paraview.simple.Interact>`
method to make the windows interactive:

```python
ps.Interact()
```

## ParaView EGL version

For older ParaView versions,
if you want to use it on a remote server,
you might want to install the
[`EGL` version](https://www.paraview.org/paraview-docs/v5.13.3/cxx/Offscreen.html):

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

## Compile ParaView from source

If you need ParaView with MPI support
(e.g. on a cluster),
and none is available,
you can compile ParaView from source following this script:

```shell
# Load prerequisite modules, depends on the cluster
export PARAVIEW_MODULES="python/3.11.6 gcc/13.1.0 cmake/3.27.7 openmpi/4.1.5-zen4"
module load $PARAVIEW_MODULES

# Clone ParaView repo
git clone --recursive https://gitlab.kitware.com/paraview/paraview.git
git -C paraview checkout v6.0.1
git -C paraview submodule update --init --recursive

# Compile ParaView
cmake -S paraview -B paraview_build \
      -DPARAVIEW_USE_PYTHON=ON \
      -DPARAVIEW_USE_MPI=ON \
      -DPARAVIEW_USE_QT=OFF \
      -DCMAKE_BUILD_TYPE=Release
make -C paraview_build -j 8

# Check if installation succeeded
cd paraview_build/bin
ls
./pvpython --version
./pvbatch --version
./pvpython -c "import sys; print(sys.executable, sys.version)"
echo "ParaView is installed in $(pwd)"
cd ../..

# Create Python venv
./paraview_build/bin/pvpython -m venv venv/paraview
source venv/paraview/bin/activate
python -c "import sys; print(sys.executable, sys.version)"

# Install sapphireppplot
pip install git+https://github.com/sapphirepp/sapphireppplot.git

# Test installation
./paraview_build/bin/pvbatch --venv=venv/paraview -c "from sapphireppplot import vfp"
```

You can now use ParaView in one of the following ways:

```shell
module load $PARAVIEW_MODULES
source /path/to/venv/paraview/bin/activate

python script.py

/path/to/paraview_build/bin/pvbatch --venv=/path/to/venv/paraview script.py

mpirun -np 4 /path/to/paraview_build/bin/pvbatch --venv=/path/to/venv/paraview script.py
```

If you run into problems, you can troubleshoot using the
[ParaView documentation](https://www.paraview.org/paraview-docs/latest/cxx/md__builds_gitlab-kitware-sciviz-ci_Documentation_dev_build.html)
and the
[conda recipe](https://github.com/conda-forge/paraview-feedstock/blob/main/recipe/build.sh)
as reference.

## Further resources

- [Sapphire++ ParaView Python introduction](https://sapphirepp.org/latest/paraview-python.html)
- [ParaView User's Guide on `pvpython`](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
- [ParaView Reference Manual on `pvbatch`](https://docs.paraview.org/en/latest/ReferenceManual/parallelDataVisualization.html#sec-usingpvbatch)
- [ParaView Tutorial on Batch Python Scripting](https://docs.paraview.org/en/latest/Tutorials/SelfDirectedTutorial/batchPythonScripting.html)
- [ParaView Tutorial on Python & Batch: ParaView & Python](https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/pythonAndBatchParaViewAndPython.html)
- {pv}`paraview.simple documentation <paraview.simple.html>`
- {pv}`paraview.simple readers, sources, writers, filters and animation cues <paraview.servermanager_proxies.html>`
- [Blog post on importing Python packages in ParaView](https://mbarzegary.github.io/2022/01/03/use-python-packages-modules-in-paraview/)
