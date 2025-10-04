"""Plot quick-start example."""

import numpy as np
from sapphireppplot import vfp, numpyify


def main() -> dict:
    """Plot quick-start example."""
    plot_properties = vfp.PlotPropertiesVFP(
        dimension=2,
        momentum=True,
        color_bar_position=[0.15, 0.55],
        animation_transparent_background=True,
    )

    results_folder, prm, solution, animation_scene = vfp.load_solution(
        plot_properties,
        path_prefix="$SAPPHIREPP_RESULTS/quick-start",
    )

    layout_2d, render_view_2d = vfp.plot_f_lms_2d(
        solution,
        results_folder,
        "quick-start-2D",
        plot_properties,
        lms_index=[0, 0, 0],
        value_range=[1e-2, 10.0],
        save_animation=True,
    )

    plot_over_line_x, layout_x, line_chart_view_x = vfp.plot_f_lms_over_x(
        solution,
        results_folder,
        "quick-start-f-x",
        plot_properties,
        lms_indices=[[0, 0, 0], [1, 0, 0]],
        direction="x",
        offset=[0, 0.05, 0],
        x_label=r"$x$",
    )

    solution_scaled, plot_properties_scaled = vfp.scale_distribution_function(
        solution, plot_properties
    )

    plot_over_line_p, layout_p, line_chart_view_p = vfp.plot_f_lms_over_p(
        solution_scaled,
        results_folder,
        "quick-start-f-p",
        plot_properties_scaled,
        lms_indices=[[0, 0, 0]],
        offset=[0.1, 0, 0],
        value_range=[1e-2, 16.0],
    )

    ln_p, data = numpyify.to_numpy_1d(
        plot_over_line_p,
        array_names=["f_000"],
        x_direction=1,
        # Only use data above 2*injection momentum (p_inj = 1)
        x_min=np.log(2.0),
    )
    ln_f = np.log(data[0])

    # Calculate log-log-slope of spectrum to find the spectral index
    spectral_index = (ln_f[-1] - ln_f[0]) / (ln_p[-1] - ln_p[0])

    print(f"Spectral Index: s = {spectral_index}")

    return locals()


if __name__ in ["__main__", "__vtkconsole__"]:
    results = main()
    # Make all results available as global variables in a vtkconsole
    globals().update(results)
