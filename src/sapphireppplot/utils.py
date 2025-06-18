"""Collection of utility functions for sapphireppplot."""

import sys
import os


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

    Returns
    -------
    str
        The path to the results folder.

    Raises
    ------
    FileNotFoundError
        If results folder is not found.
    """
    results_folder = ""
    if len(sys.argv) > 1:
        results_folder = sys.argv[1]
    if not results_folder:
        results_folder = input("Path to results folder: ")

    if path_prefix and not os.path.isabs(results_folder):
        results_folder = os.path.join(path_prefix, results_folder)
    results_folder = os.path.expandvars(results_folder)
    results_folder = os.path.expanduser(results_folder)
    results_folder = os.path.abspath(results_folder)

    if not os.path.isdir(results_folder):
        raise FileNotFoundError(
            f"Results folder '{results_folder}' does not exist "
            "or is not a directory."
        )

    print(f"Using results in '{results_folder}'")
    return results_folder
