# Advanced usage

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

Starting with ParaView 6.0.0,
an off-screen version can be enabled directly during the build.

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
