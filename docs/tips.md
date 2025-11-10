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

## Further resources

- [ParaView User's Guide on `pvpython`](https://docs.paraview.org/en/latest/UsersGuide/introduction.html#getting-started-with-pvpython)
- [ParaView Reference Manual on `pvbatch`](https://docs.paraview.org/en/latest/ReferenceManual/parallelDataVisualization.html#sec-usingpvbatch)
- [ParaView Tutorial on Batch Python Scripting](https://docs.paraview.org/en/latest/Tutorials/SelfDirectedTutorial/batchPythonScripting.html)
- [ParaView Tutorial on Python & Batch: ParaView & Python](https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/pythonAndBatchParaViewAndPython.html)
- {pv}`paraview.simple documentation <paraview.simple.html>`
- {pv}`paraview.simple readers, sources, writers, filters and animation cues <paraview.servermanager_proxies.html>`
