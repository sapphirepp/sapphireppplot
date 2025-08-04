"""Collection of utility functions for sapphireppplot."""

import sys
import os
from typing import Dict, Union

ParamDict = Dict[str, Union[str, "ParamDict"]]


_results_folder_argv: int = 1
"""
Global variable to keep track which argv to use for get_results_folder.
"""


def get_results_folder(
    path_prefix: str = "", message: str = "Input path to results folder"
) -> str:
    """
    Prompts the user to specify the path to a results folder.

    If the script from command line with arguments
    it uses the first argument as the results folder path.
    Otherwise, it prompts the user to input the path manually.

    Parameters
    ----------
    path_prefix : str, optional
        Prefix for relative path.
        Note that relative path and environment variables
        are evaluated on the executing machine.
        Avoid relative path if you are connected to a data server
        with client-side execution.
    message : str, optional
        Message to be prompted for input.

    Returns
    -------
    results_folder : str
        The path to the results folder.
    #"""
    global _results_folder_argv  # pylint: disable=global-statement

    path_prefix = os.path.expandvars(path_prefix)
    path_prefix = os.path.expanduser(path_prefix)
    path_prefix = os.path.abspath(path_prefix)

    results_folder = ""
    if len(sys.argv) > _results_folder_argv:
        results_folder = sys.argv[_results_folder_argv]
        _results_folder_argv += 1
    if not results_folder:
        results_folder = input(f"{message} \n({path_prefix}): ")
    results_folder = os.path.expandvars(results_folder)
    results_folder = os.path.expanduser(results_folder)
    if path_prefix and not os.path.isabs(results_folder):
        results_folder = os.path.join(path_prefix, results_folder)

    print(f"Using results in '{results_folder}'")
    return results_folder


def prm_to_dict(prm_lines: list[str]) -> ParamDict:
    """
    Convert parameter file to a dict.

    Parameters
    ----------
    prm_lines : list[str]
        List of line in the parameter file.

    Returns
    -------
    ParamDict
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
