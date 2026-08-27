# FAQ

## Why is my 2D or 3D plot not working?

For stretched grids, ParaView can sometimes have problems displaying 2D or 3D plots.
This is especially likely when coordinates,
such as $\ln(p)$ and $x$,
have very different scales.

By default, ParaView assumes that all axes use the same scale.
For example, if

$$
x \in [-15000, 100]
$$

and

$$
\ln(p) \in [-2.3, 4.6],
$$

as in the [Steady-state parallel shock](https://sapphirepp.org/latest/steady-state-parallel-shock.html) example,
the $\ln(p)$ range is much smaller than the $x$ range.

To compensate for this visual difference,
scale the $\ln(p)$ axis using {prop}`axes_scale`:

```python
plot_properties.axes_scale = (1.0, 2e3, 1.0)
```

The entries specify the visual scaling of the $X$, $Y$, and $Z$ axes:

- The first entry scales the $X$ axis, corresponding to $x$.
- The second entry scales the $Y$ axis, corresponding to $\ln(p)$.
- The third entry scales the $Z$ axis, which is not used in this example.

With the setting above, the $\ln(p)$ axis is displayed approximately over the range

$$
-2.3 \times 2 \cdot 10^3 = -4600
$$

to

$$
4.6 \times 2 \cdot 10^3 = 9200.
$$

This scaling is visual only: the displayed axis labels and the underlying data remain unchanged.

## Why is `plot_over_line` not working?

Sometimes a line plot in ParaView produces no results.
This can happen when using functions such as:

- {sap}`transform.plot_over_line()`
- {sap}`vfp.plot_f_lms_over_x()`
- {sap}`vfp.plot_f_lms_over_p()`
- {sap}`mhd.plot_quantities_over_x()`

Try the following steps:

1. Check that `offset` is inside the simulation domain.

   For a VFP simulation, the coordinates depend on the simulation settings:

   - The first `dim_cs` coordinates refer to $x$, $y$, and $z$.
   - If the simulation is momentum-dependent, the `dim` coordinate refers to $\ln(p)$,
     or to $p$ when `linear_p` is enabled.

2. Set {prop}`sampling_pattern` to `uniform`.

   For highly stretched grids,
   such as shock grids,
   ParaView may have trouble identifying cell centres automatically.
   After confirming that the plot works with `uniform` sampling,
   you can switch back to `center` sampling and adjust {prop}`sampling_resolution`.
   The value for this setting is highly problem dependent and can vary by orders of magnitudes.
   Just try out different values between `1e10` and `1e-10` to get a feeling.

3. Adjust the `value_range`.

   As a first test, omit `value_range` and let ParaView determine the range automatically.
   Logarithmic plots may produce a warning and be changed to a linear scale.
   Once you have found a suitable range, specify it in the plotting function
   and switch back to logarithmic scaling if needed.

As a general rule, first inspect the complete 2D or 3D dataset
to understand the simulation domain and results.
If that also fails,
see [Why is my 2D or 3D plot not working?](#why-is-my-2d-or-3d-plot-not-working).

## How can I interact with ParaView preview windows?

When using the interactive Python shell,
plotting scripts may open ParaView preview windows
that cannot be interacted with or closed.

In this case,
call {pv}`paraview.simple.Interact() <paraview.simple.html#paraview.simple.Interact>`:

```python
ps.Interact()
```

## How can I disable the preview windows?

By default, ParaView opens a preview window for each plot
(see previous question).
To avoid this,
run the script with `pvbatch` instead of `python` or `pvpython`:

```shell
pvbatch script.py args
```

`pvbatch` executes the script in batch mode
and therefore opens no windows at all.

## Why do I get an `AttributeError` when running scripts with `pvbatch`?

If your script fails with an error like

```text
AttributeError: 'paraview.modules.vtkRemotingServerManager.vtkSMProxy' object has no attribute 'UpdateAnimationUsingDataTimeSteps'
```

this usually indicates that `pvbatch` mixes two different ParaView installations.
This can happen when linking the `sapplot` environment to ParaView,
`pvbatch --venv=/path/to/venv/sapplot`
(see [Link package to an existing ParaView installation using `venv`](installation.md)),
if ParaView is also installed inside the `venv`.
In that case,
the external `pvbatch` may pick up the `paraview` Python package of the `venv`
instead of the one bundled with your ParaView installation,
and the mismatched versions may lead to conflicts.

Make sure that the `venv` does **not** contain a ParaView installation installed via `conda`,
and that only `sapphireppplot` and its dependencies are installed.

## Why does `mpirun` fail when the `sapplot` environment is activated?

If you run a command (e.g. `sapphirepp`) with `mpirun`
while the `sapplot` environment is activated,
it might fail with an MPI error.

This is usually caused by a conflict of MPI versions,
with an MPI installation in the `venv`.
In particular, this happens if `mpi4py` is installed in the environment.

Either deactivate the environment
before executing other programs with `mpirun`,
or remove the `mpi` packages from the `venv` if they are not needed.

## How do I use LaTeX in the `time_format` property?

The {prop}`time_format` string is a format string:
the placeholder `{time}` is replaced by the current simulation time
and can be given a format specifier, e.g. `{time:.2f}`.
All other braces,
such as those used for LaTeX super- and subscripts,
must be escaped by doubling them,
i.e. `{{` and `}}`.
Otherwise, you will get an error like

```text
Invalid format specified '$\gamma_{\rm max} t = {time:.2f}$'
Details: invalid format string
```

For example,

```python
plot_properties.time_format = r"$\gamma_{\rm max} t = {time:.2f}$"
```

raises the error above, while

```python
plot_properties.time_format = r"$\gamma_{{\rm max}} t = {time:.2f}$"
```

renders $\gamma_{\rm max} t = 12.34$.

More information on the format specifiers
can be found in the [fmt documentation](https://fmt.dev/latest/syntax/),
which ParaView uses for this property.
