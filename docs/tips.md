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

## Further resources

- [Sapphire++ ParaView Python introduction](https://sapphirepp.org/latest/paraview-python.html)
- [ParaView User's Guide on `pvpython`](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
- [ParaView Reference Manual on `pvbatch`](https://docs.paraview.org/en/latest/ReferenceManual/parallelDataVisualization.html#sec-usingpvbatch)
- [ParaView Tutorial on Batch Python Scripting](https://docs.paraview.org/en/latest/Tutorials/SelfDirectedTutorial/batchPythonScripting.html)
- [ParaView Tutorial on Python & Batch: ParaView & Python](https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/pythonAndBatchParaViewAndPython.html)
- {pv}`paraview.simple documentation <paraview.simple.html>`
- {pv}`paraview.simple readers, sources, writers, filters and animation cues <paraview.servermanager_proxies.html>`
- [Blog post on importing Python packages in ParaView](https://mbarzegary.github.io/2022/01/03/use-python-packages-modules-in-paraview/)
