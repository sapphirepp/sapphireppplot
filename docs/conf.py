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
    "sphinx.ext.extlinks",
    "myst_parser",
    "nbsphinx",
    "sphinx_copybutton",
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
napoleon_use_rtype = False

extlinks = {
    "pv": (
        "https://www.paraview.org/paraview-docs/latest/python/%s",
        "%s",
    ),
    "ps": (
        "https://www.paraview.org/paraview-docs/latest/python/paraview.simple.__init__.%s.html",
        "paraview.simple.%s",
    ),
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

html_static_path = ["_static"]
# html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"
