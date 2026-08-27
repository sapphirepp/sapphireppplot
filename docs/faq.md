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
