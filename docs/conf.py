"""Configure sphinx."""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Add project root to sys.path --------------------------------------------
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sapphireppplot"
copyright = "2025, Florian Schulze"
author = "Florian Schulze"
version = "latest"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    # "sphinx.ext.autosummary",
    "myst_parser",
    "nbsphinx",
    "sphinx_multiversion",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}

# Allow Markdown files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

# -- Options for sphinx-multiversion -----------------------------------------
# https://sphinx-contrib.github.io/multiversion/main/configuration.html

smv_tag_whitelist = r"^v\d+\.\d+\.\d+$"
smv_branch_whitelist = r"main"
smv_released_pattern = r"^refs/tags/v\d+\.\d+\.\d+$"
