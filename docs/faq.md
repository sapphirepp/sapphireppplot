# FAQ

## How can I interact with the ParaView preview windows?

When using the interactive Python shell,
the plotting scripts may open ParaView preview windows
that can not be interacted with or closed.
In this case, you can use the
{pv}`paraview.simple.Interact() <paraview.simple.html#paraview.simple.Interact>`
method to make the windows interactive:

```python
ps.Interact()
```
