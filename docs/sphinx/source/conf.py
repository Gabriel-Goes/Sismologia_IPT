# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ClassificadorSismologico Refatoracao'
copyright = '2026, Gabriel Goes Rocha de Lima'
author = 'Gabriel Goes Rocha de Lima'

version = '0.1'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_baseurl = os.environ.get('SPHINX_HTML_BASEURL', '')
