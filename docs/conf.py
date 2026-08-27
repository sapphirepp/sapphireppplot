"""Configure sphinx."""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Add project root to sys.path --------------------------------------------
import os
import sys
from docutils import nodes
from sphinx import addnodes

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


# -- Add custom roles --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/development/tutorials/extending_syntax.html#the-setup-function


def sap_role(
    name, rawtext, text, lineno, inliner, options={}, content=[]  # noqa
):  # noqa
    """
    Shorthand role for sapphireppplot functions.

    Usage: {sap}`utils.match_index()`
    Expands to: {py:func}`utils.match_index() <sapphireppplot.utils.match_index()>`
    """
    full_target = f"sapphireppplot.{text}"

    ref_node = addnodes.pending_xref(
        rawtext,
        refdomain="py",
        reftype="func",
        reftarget=full_target,
        refwarn=True,
    )

    ref_node += nodes.literal(rawtext, text, classes=["xref", "py", "py-func"])

    return [ref_node], []


def prop_role(
    name, rawtext, text, lineno, inliner, options={}, content=[]  # noqa
):  # noqa
    """
    Shorthand role for PlotProperties attributes.

    Usage: {prop}`series_names`
    Expands to: {py:attr}`PlotProperties.series_names <sapphireppplot.plot_properties.PlotProperties.series_names>`
    """
    full_target = f"sapphireppplot.plot_properties.PlotProperties.{text}"

    ref_node = addnodes.pending_xref(
        rawtext,
        refdomain="py",
        reftype="attr",
        reftarget=full_target,
        refwarn=True,
    )

    display_text = f"PlotProperties.{text}"
    ref_node += nodes.literal(
        rawtext, display_text, classes=["xref", "py", "py-attr"]
    )

    return [ref_node], []


def setup(app):  # noqa
    app.add_role("sap", sap_role)
    app.add_role("prop", prop_role)
