"""Create Sapphire++ - Plot logo."""

import os
import paraview.simple as ps
import paraview.util
from sapphireppplot.plot_properties import PlotProperties
from sapphireppplot import utils, pvplot


def main() -> dict:
    """Create Sapphire++ - Plot logo."""
    plot_properties = PlotProperties(
        representation_type="UniformGridRepresentation",
        preview_size_2d=[128, 128],
        screenshot_transparent_background=True,
        series_names=["PNGImage"],
        labels={"PNGImage": "Sapphire++"},
        grid_labels=["", "", ""],
        color_bar_length=0,
        color_map="Black, Blue and White",
        text_color=[0, 0, 0],
        grid_color=[0, 0, 0],
        text_size=0,
        label_size=0,
        camera_view_2d=(True, 0.9),
    )

    results_folder = utils.get_results_folder(
        path_prefix="$SAPPHIREPP_PLOT/docs/_static",
        results_folder=".",
    )

    file_name = "sapphire_logo_without_text.png"
    # region Load png
    search_pattern = os.path.join(results_folder, file_name)
    png_file = paraview.util.Glob(search_pattern)
    if not png_file:
        raise FileNotFoundError(f"No file found matching '{search_pattern}'")
    print(f"Load image '{search_pattern}'")

    solution = ps.PNGSeriesReader(
        registrationName=file_name,
        FileNames=png_file,
    )
    solution.UpdatePipelineInformation()
    # endregion

    # region Plot logo
    layout = ps.CreateLayout("logo")
    render_view = pvplot.plot_render_view_2d(
        solution,
        layout,
        "PNGImage",
        plot_properties=plot_properties,
    )

    solution_display = ps.GetRepresentation(solution, view=render_view)
    solution_display.Representation = "Slice"
    solution_display.MapScalars = 1

    pvplot.save_screenshot(layout, results_folder, "logo", plot_properties)
    # endregion

    print("Convert logo to favicon using:")
    print(
        f"  magick {results_folder}/logo.png -resize 32x32 {results_folder}/favicon.ico"
    )

    return locals()


if __name__ in ["__main__", "__vtkconsole__"]:
    results = main()
    # Make all results available as global variables in a vtkconsole
    globals().update(results)
