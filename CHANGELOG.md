# Release Notes

## Changes: 2.0.0

- **Breaking change:** Colors are now specified with matplotlib colors.
  `PlotProperties` attributes and function arguments
  now use matplotlib color types (e.g. `"black"`, `"#ff0000"`, or RGB tuples)
  instead of lists of RGB strings.
- **Breaking change:** Coordinates, offsets, and ranges are now passed as tuples.
  Arguments that previously accepted lists,
  e.g. `direction`, `offset`, `normal`, `origin`, `point`, or `x_range`,
  now accept tuples.
- The Python requirement was lowered to 3.11.
- The package now enforces ParaView 6.0 compatibility.

### VFP

- **Breaking change:** The scaled distribution function is now named `F`.
  The base name `p^s f` was replaced by `F`
  for the scaled distribution function.
- **Breaking change:** Removed `PlotPropertiesVFP.f_lms_label()` and `PlotPropertiesVFP.scale_by_spectral_index()`.
  The scaling of the distribution function,
  including the labels,
  is now handled directly by `vfp.scale_distribution_function()`.
- Add a `normalization` argument to `scale_distribution_function`.
  The scaled distribution function is now `F = N * p^s f`
  with the normalization `N`.
- `scale_distribution_function` now uses the `transform.calculator` calculator.
- Add phase space surface plots
  - `plot_phase_space_surface`: A 2D `cos(theta) - phi` plot of the phase space distribution
  - `plot_elevated_phase_space_surface`: An elevated surface plot of the phase space distribution
  - `plot_phase_space_spherical_density_map`: A spherical density map of the phase space distribution
  The data can be loaded with `load_probe_location_surface`
  and `load_probe_location_spherical_density`.
  The spherical probe now supports a custom resolution.
- Add `PlotPropertiesVFP.convert_lnp_to_p()` and `PlotPropertiesVFP.convert_lnp_to_log10p()`.
  These convert the momentum axis from `ln(p)` to `p` (LineChartView)
  or to `log10(p)` (RenderView).
- Add a `layout` argument to the plot functions.
  Plots can now be added to an existing layout.
- Add a `camera_direction` argument to the spherical phase space plot.
- Fix: The numeric and the exact solution are now scaled consistently.
- Fix: Correct 3D plots.

### MHD

- **Breaking change:** Renamed the Alfvén speed `c_a` to `c_A`.
- Add `compute_mach_number`.
  Compute the Mach number `M = |u| / a_s` with the sound speed `a_s`.
- Add `compute_alfven_mach_number`.
  Compute the Alfvén Mach number `M_A = |u| / c_A`.
- `compute_normalized_magnetic_divergence` can now use a global reference field.
  A new `b_0` argument computes `|div b| * dx / b_0`
  instead of the local `|div b| * dx / |b|`.
- Add `extract_slices_from_3d`.
  Create and save `x-y`, `x-z`, and `y-z` slices of a 3D solution.
- Add `save_to_dat`.
  Save cell-centred data as `.dat` files with a history file `.hst`.
- Add the entropy `S` to `PlotPropertiesMHD`.
- Add `show_time` to `plot_quantities_over_x`.
- Add `x_label` to `plot_quantities_1d`.
- Fix: `compute_kinetic_energy` now also works for exact solutions.
- Fix: `PlotPropertiesMHD` now supports `line_colors`.
- Fix: Simplify and correct the formulas of the derived quantities.

### SATANIC

- Add a new `satanic` module.
  The new module provides plotting routines for results from SATANIC
  (Solving Acceleration, Transport And Non-thermal Interactions in star Clusters).
  It provides
  - `load_solution` to load the results,
  - 1D plots `plot_f_over_r`, `plot_f_over_p`, and `plot_f_over_mu`,
  - 2D and 3D plots `plot_f_2d` and `plot_f_3d`,
  - matplotlib plots `matplot_f_over_r`, `matplot_f_over_p`, `matplot_f_over_mu`,
    `matplot_f_r_p`, and `matplot_f_r_mu`,
  - the slices `slice_plane_r_p` and `slice_plane_r_mu`,
  - `to_numpy` to extract the data,
  - and `convert_mu_to_theta` to convert the `mu` axis to `theta`.
- Add `unit_r`, `unit_p`, `unit_t`, and `update_properties()` to `PlotPropertiesSatanic`.
  The units are used in the axis labels.

### pvload

- **Breaking change:** The animation scene is now updated with the scaled time steps.
  `scale_time_steps` now takes an `animation_scene` argument
  and updates the AnimationScene to the scaled time steps.
- Add `load_csv`.
  Load `.csv` files as a ParaView source.
- Add a `registration_name` argument to the `load_solution_*` functions.
  `load_solution` now uses the `Simulation identifier` parameter as registration name.
- Add a `results_folder` argument to `load_solution`.
- Skip the time scaling for steady-state solutions.
  The time steps are no longer scaled if there is only one time step.
- Add an option to skip the parameter file loading.
  Set `parameter_file_name = None` to skip it.
- Fix: `.pvtu` files now use the time array.
- Crinkle extracts can now be saved in `.pvtu` format.

### pvplot

- **Breaking change:** `show_stream_tracer` was renamed to `show_overlay_2d`.
  The function now shows any overlay,
  e.g. stream tracers or contour lines,
  in a 2D render view.
- Add `save_view`.
  Save a ParaView view as vector graphics (`svg`, `eps`, `pdf`)
  or as a table (`csv`).
  Note that this feature is unstable and can lead to crashes.
- Add `show_spread_sheet`.
  Show the data of a source as a spreadsheet in ParaView.
- Add `show_outline`.
  Show an outline of the solution in a render view.
- Add a `line_width` argument to `show_overlay_2d`.
- Fix: Text, e.g. the time annotation, now uses the configured font family
  and is saved as text in vector graphics.
- Fix: Plots can now be added to existing plots.

### transform

- **Breaking change:** `clip_area` now uses `x_range`, `y_range`, and `z_range`.
  The arguments `min_x`, `max_x`, `min_y`, and `max_y` were replaced by ranges
  that default to the full range of the solution.
- **Breaking change:** `stream_tracer` now takes `plot_properties_in`
  and returns a tuple of the source and the `PlotProperties`.
- **Breaking change:** `save_extracts` now takes an `animation_scene` argument.
  The default file format for extracts is now `pvtp`,
  and slices are no longer crinkled by default.
- **Breaking change:** Default line styles and colors are no longer forced.
  They are now set by `PlotProperties`.
- Add `contour_lines`.
  Create contour lines of a quantity.
  They can be added to a 2D render view with `pvplot.show_overlay_2d()`.
- Add a `frame_window` argument to `save_extracts`.
  The range of timesteps can now be selected.
- Fix: The calculator uses less memory.
- Fix: Extractors now support compression.
- Fix: `integrate_variables` now also works for 2D extracts.

### numpyify

- **Breaking change:** `to_numpy_time_steps`, `to_numpy_time_steps_2d`,
  and `to_numpy_time_steps_3d` now use the exact time steps of the animation scene.
  An `animation_scene` argument was added,
  which ensures that the correct (e.g. scaled) time steps are used.
- Add the time to the result of `to_numpy_1d`.
- Add a warning if the array names are unknown.

### PlotProperties

- Add `set_style()`.
  Set the `PlotProperties` according to a matplotlib style sheet,
  e.g. `MNRAS`, `beamerposter_A0`, `beamer_mpik_169`, or `notebook`.
  This ensures consistent fonts, figure sizes, and line widths
  for a specific journal or presentation.
- Add `font_family`, `default_line_width`, `color_bar_thickness`,
  `color_bar_orientation`, and `background_color`.
- Add `line_widths`.
  Set different line widths for the different series.
- Add custom axes ticks and custom axis labels.
- Add `export_precision`.
  The precision of the exported data, e.g. for `save_view`.
- Animations can now be deactivated by setting `animation_frame_stride = -1`.
- `time_format` now defaults to the LaTeX format.
- Fix: Correct the `LineChartView` labels and lines.

### utils

- Add `colorblind_colors()`.
  A colorblind-friendly color palette.
- Add `sapphirepp_colors()`.
  The Sapphire++ color palette (by Thibault Vieu).
- Add `set_matplotlib_style()`.
  Set a matplotlib style sheet.
  The `disable_tex` flag allows to disable the TeX rendering.

### Styles

- Add matplotlib style sheets: `MNRAS`, `beamerposter_A0`, `beamer_mpik_169`, and `notebook`.
  The style sheets set consistent fonts, figure sizes, and line widths
  for publications and presentations.
  They can be applied with `PlotProperties.set_style()` or `utils.set_matplotlib_style()`.
- Fix: Figures with transparent backgrounds are now saved correctly.

### Documentation

- Split the "Tips" page into `FAQ`, `Advanced usage`, and `Further resources`.
- Add new FAQ entries.
- Clarify the installation steps.
  Add instructions for virtual environments
  and for compiling ParaView from source.
- The Jupyter tutorial now uses the `set_style` functions.

### Build & Testing

- Check the types with `mypy` in the test suite.
- The example scripts are now tested.

**Full Changelog**: https://github.com/sapphirepp/sapphireppplot/compare/v1.0.0...v2.0.0
