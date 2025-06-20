"""Collection of utility functions for sapphireppplot."""

import sys
import os


_results_folder_argv: int = 1
"""
Global variable to keep track which argv to use for get_results_folder.
"""


def get_results_folder(path_prefix: str = "") -> str:
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
        results_folder = input(f"Path to results folder ({path_prefix}): ")
    results_folder = os.path.expandvars(results_folder)
    results_folder = os.path.expanduser(results_folder)
    if path_prefix and not os.path.isabs(results_folder):
        results_folder = os.path.join(path_prefix, results_folder)

    print(f"Using results in '{results_folder}'")
    return results_folder
