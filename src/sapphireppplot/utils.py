"""Collection of utility functions for sapphireppplot."""

import sys
import os
from typing import cast, Optional, Any, Dict, Literal
from collections.abc import Sequence
from importlib.resources import files
from matplotlib.typing import ColorType
from cycler import cycler
import numpy as np

# ParamDict = Dict[str, Union[str, "ParamDict"]] # Confuses autodoc_typehints
ParamDict = Dict[str, Any]


_results_folder_argv: int = 1
"""
Global variable to keep track which argv to use for get_results_folder.
"""


def get_results_folder(
    path_prefix: str = "",
    results_folder: str = "",
    message: str = "Input path to results folder",
) -> str:
    """
    Prompts the user to specify the path to a results folder.

    If the script from command line with arguments
    it uses the first argument as the results folder path.
    Otherwise, it prompts the user to input the path manually.

    Parameters
    ----------
    path_prefix
        Prefix for relative path.
        Note that relative path and environment variables
        are evaluated on the executing machine.
        Avoid relative path if you are connected to a data server
        with client-side execution.
    results_folder
        The path to the results folder.
    message
        Message to be prompted for input.

    Returns
    -------
    results_folder : str
        The path to the results folder.
    """
    global _results_folder_argv  # pylint: disable=global-statement

    path_prefix = os.path.expandvars(path_prefix)
    path_prefix = os.path.expanduser(path_prefix)
    path_prefix = os.path.abspath(path_prefix)

    if not results_folder and len(sys.argv) > _results_folder_argv:
        results_folder = sys.argv[_results_folder_argv]
        _results_folder_argv += 1
    if not results_folder:
        results_folder = input(f"{message} \n({path_prefix}): ")
    results_folder = os.path.expandvars(results_folder)
    results_folder = os.path.expanduser(results_folder)
    if path_prefix and not os.path.isabs(results_folder):
        results_folder = os.path.join(path_prefix, results_folder)
    results_folder = os.path.normpath(results_folder)

    print(f"Using results in '{results_folder}'")
    return results_folder


def prm_to_dict(prm_lines: list[str]) -> ParamDict:
    """
    Convert parameter file to a dict.

    Parameters
    ----------
    prm_lines
        List of line in the parameter file.

    Returns
    -------
    prm_dict : ParamDict
        Dictionary representing the parameter file structure.
        Values are always given as strings.
        Subsections are given as dicts.
    """
    prm_dict: ParamDict = {}

    while prm_lines:
        line = prm_lines.pop(0)
        # Remove comments
        line = line.split("#", maxsplit=1)[0].strip()
        if not line:
            continue

        if line.startswith("set "):
            key_value = line.removeprefix("set").split("=")
            prm_dict[key_value[0].strip()] = key_value[1].strip()
        elif line.startswith("subsection "):
            subsection = line.removeprefix("subsection ")
            prm_dict[subsection] = prm_to_dict(prm_lines)
        elif line == "end":
            return prm_dict
        else:
            print(f"Unknown line: {line}")

    return prm_dict


def match_index(list_in: Sequence[Any], target: Any) -> int:
    """
    Find index ``i`` where ``list_in[i] = target``.

    Parameters
    ----------
    list_in
        List/array of values to search.
    target
        Target value to find.

    Returns
    -------
    index : int
        Index ``i``.

    Raises
    ------
    ValueError
        Raises an error if the ``target`` can not be found in ``list_in``
        or multiple matches exist.
    """
    list_np = np.array(list_in)
    matched_indices = np.where((list_np == target).all(axis=1))[0]

    if matched_indices.size == 0:
        raise ValueError(f"No match for {target}.")
    if matched_indices.size != 1:
        raise ValueError(
            f"Multiple matches for {target} at indices {matched_indices}"
        )

    return cast(int, matched_indices[0])


def find_closest_index(
    array: Sequence[Any] | np.ndarray,
    target: Any,
    print_index: bool = False,
) -> int:
    """
    Find closest index ``i`` to ``array[i] = target`` in a sorted array.

    Parameters
    ----------
    array
        Sorted array of values to search.
    target
        Target value to find.
    print_index
        Print the found index and match to the console?

    Returns
    -------
    index : int
        Index ``i``.
    """
    index = np.searchsorted(array, target, side="left")
    if index > 0 and (
        index == len(array)
        or np.abs(target - array[index - 1]) < np.abs(target - array[index])
    ):
        index -= 1

    # Alternative for unsorted arrays:
    # index = (np.abs(array - target)).argmin()

    if print_index:
        print(
            f"{index} is closest index to {target}: "
            f"array[{index}] = {array[index]}"
        )
    return cast(int, index)


def sapphirepp_colors() -> list[ColorType]:
    """
    Get a list of six colors in the Sapphire++ design for line plots.

    Thanks to Thibault Vieu for selecting the colors!

    Returns
    -------
    sapphirepp_colors
        A list of six colors in the Sapphire++ design.
    """
    return [
        "#c4a5b6",
        "#78539f",
        "#38d9f3",
        "#317caf",
        "#031330",
        "#5c6577",
    ]


def colorblind_colors() -> list[ColorType]:
    """
    Get a list of colorblind friendly colors for line plots.

    Uses the seaborn ``colorblind`` color palette,
    see `seaborn documentation <https://seaborn.pydata.org/generated/seaborn.color_palette.html>`_.

    Returns
    -------
    sapphirepp_colors
        A list of ten colorblind friendly colors.
    """
    return [
        "#0173b2",
        "#de8f05",
        "#029e73",
        "#d55e00",
        "#cc78bc",
        "#ca9161",
        "#fbafe4",
        "#949494",
        "#ece133",
        "#56b4e9",
    ]


def set_matplotlib_style(
    style: Literal["notebook", "MNRAS"] = "notebook",
    font_scale: float = 1.0,
    color_palette: (
        Literal["colorblind", "sapphirepp"] | list[ColorType]
    ) = "colorblind",
    disable_tex: bool = False,
    custom_rc: Optional[dict[str, Any]] = None,
) -> None:
    """
    Set ``matplotlib.rcParams`` according to a style.

    This can be used to set the style for a specific journal.

    Parameters
    ----------
    style
        Style of to use.

        - ``notebook``: Style optimised for Jupyter notebooks
        - ``MNRAS``: Style for MNRAS article
    font_scale
        Scaling factor for the font in titles, labels and legends.
    color_palette
        Color pallet to use for line colors.

        - ``colorblind``: :py:func:`colorblind_colors`
        - ``sapphirepp``: :py:func:`sapphirepp_colors`
    disable_tex
        Some styles use LaTeX to render text.
        This can lead to rendering errors
        if no working LaTeX installation is provided
        or required packages are missing.
        To avoid this isse, you can disable LaTeX rendering.
        Note however, that this can drastically alter the style.
    custom_rc
        Custom overwrite of ``rcParams``, applied after scaling.

    See Also
    --------
    sapphireppplot.plot_properties.PlotProperties.set_style:
        Set style for ParaView plots.
    """
    import matplotlib as mpl  # pylint: disable=import-outside-toplevel
    import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

    base = files("sapphireppplot.styles").joinpath("base.mplstyle")
    if not base.is_file():
        raise FileNotFoundError(f"Base style not found: {base}")
    theme = files("sapphireppplot.styles").joinpath(f"{style}.mplstyle")
    if not theme.is_file():
        available = [
            f.name.replace(".mplstyle", "")
            for f in files("sapphireppplot.styles").iterdir()
            if f.name.endswith(".mplstyle") and f.name != "base.mplstyle"
        ]
        raise FileNotFoundError(
            f"Style '{style}' not found. Available styles: {available}"
        )
    # Styles can also be used via: plt.style.use("sapphireppplot.styles.base")
    plt.style.use([str(base), str(theme)])

    colors = None
    color_palettes: dict[str, list[ColorType]] = {
        "colorblind": colorblind_colors(),
        "sapphirepp": sapphirepp_colors(),
    }
    if isinstance(color_palette, list):
        colors = color_palette
    elif color_palette in color_palettes:
        colors = color_palettes[color_palette]
    else:
        raise KeyError(
            f"Color palette '{color_palette}' not found. "
            f"Available color palettes: {list(color_palettes.keys())}"
        )
    if colors is not None:
        mpl.rcParams["axes.prop_cycle"] = cycler(color=colors)

    if font_scale != 1.0:
        for key in (
            "font.size",
            "axes.titlesize",
            "axes.labelsize",
            "legend.title_fontsize",
            "legend.fontsize",
            "xtick.labelsize",
            "ytick.labelsize",
        ):
            # Do not scale if 'medium', 'small', ...
            if isinstance(mpl.rcParams[key], float):
                mpl.rcParams[key] *= font_scale

    if disable_tex:
        mpl.rcParams.update({"text.usetex": False, "text.latex.preamble": ""})

    if custom_rc:
        mpl.rcParams.update(custom_rc)  # type: ignore
