# Configuration file for the Sphinx documentation builder.
# Documentation: https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import shutil


# -- Path Setup ---------------------------------------------------------------
def add_to_sys_path(path):
    """Add a directory to sys.path and print the result."""
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)
        print(f"Added to sys.path: {abs_path}")


# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
add_to_sys_path(project_root)


# -- Project Information ------------------------------------------------------
project = "VITAL"
copyright = (
    "2025, National Technology & Engineering Solutions of Sandia, LLC (NTESS). "
    "Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software."
)
author = "Sandia National Laboratories"
release = "1.0.0"


# -- General Configuration ----------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # Automatically document Python modules
    "sphinx.ext.napoleon",      # Support for Google-style and NumPy-style docstrings
    "sphinx.ext.viewcode",      # Add links to highlighted source code
    "sphinx.ext.mathjax",       # Render mathematical expressions using MathJax
    "sphinx.ext.autosummary",   # Automatically generate summary tables
    "sphinx.ext.intersphinx",   # Link to external project documentation
    "nbsphinx",                 # Enables Jupyter Notebook rendering
]

autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_ignore_modules = ["vital.constGlobal", "vital.constUnitConvert"]

templates_path = ["_templates"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    "examples/Old",
    "examples/Old/**",
]


# -- HTML Output Configuration ------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = []
html_show_sourcelink = False


# -- Autodoc Configuration ----------------------------------------------------
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "special-members": "__init__",
    "show-inheritance": True,
}
autodoc_class_signature = "separated"


# -- Napoleon Configuration ---------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
add_module_names = False


# -- Syntax Highlighting ------------------------------------------------------
highlight_language = "python3"
rst_prolog = """
.. role:: python(code)
   :language: python
"""


# -- MathJax Configuration ----------------------------------------------------
mathjax3_config = {
    "TeX": {
        "equationNumbers": {"autoNumber": "AMS"},
    }
}


# -- Intersphinx Configuration ------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
}


# -- Suppress Warnings --------------------------------------------------------
suppress_warnings = [
    "toc.not_included",
]


# -- nbsphinx Configuration ---------------------------------------------------
# Use "never" for reliable documentation builds because several tutorials use
# NOAA web services. If notebook outputs are desired in the HTML docs, save the
# outputs in the notebooks before building.
#
# Other possible values:
#   "auto"   - execute notebooks only if no outputs are present
#   "always" - always execute notebooks during docs build
nbsphinx_execute = "always"
nbsphinx_allow_errors = True


# -- File Operations ----------------------------------------------------------
def copy_directory(source, target, ignore_func=None):
    """Safely copy a directory, removing the target if it exists."""
    try:
        print(f"Removing existing directory: {target}")
        shutil.rmtree(target, ignore_errors=True)

        print(f"Copying from {source} to {target}")
        shutil.copytree(source, target, ignore=ignore_func)
    except Exception as e:
        print(f"Error during file operation: {e}")


def exclude_non_ipynb_files(directory, contents):
    """Exclude non-Jupyter Notebook files and old/development examples."""
    excluded = []

    for name in contents:
        if name == "Old":
            excluded.append(name)
        elif not name.endswith(".ipynb"):
            excluded.append(name)

    return excluded


def exclude_data_files(directory, contents):
    """Exclude old/development data and local system files from docs copy."""
    excluded = []

    for name in contents:
        if name in {"OldFile", ".DS_Store", "__pycache__"}:
            excluded.append(name)
        elif name.endswith(".pyc"):
            excluded.append(name)

    return excluded


# Copy example notebooks into the Sphinx source tree.
# The copied directory is removed after HTML build by docs/Makefile.
source_example = os.path.join(project_root, "example")
target_example = os.path.join(project_root, "docs/source/examples")
copy_directory(
    source_example,
    target_example,
    ignore_func=exclude_non_ipynb_files,
)


# Copy data files into the Sphinx source tree.
# This supports notebook rendering with relative paths such as "../data/...".
# The copied directory is removed after HTML build by docs/Makefile.
source_data = os.path.join(project_root, "data")
target_data = os.path.join(project_root, "docs/source/data")
copy_directory(
    source_data,
    target_data,
    ignore_func=exclude_data_files,
)


print("Configuration setup complete!")