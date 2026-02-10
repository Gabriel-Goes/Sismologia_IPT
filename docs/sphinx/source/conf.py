# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
from pathlib import Path

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
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
autosectionlabel_prefix_document = True

# Hybrid mode: generate missing API pages but preserve manually edited ones.
autosummary_generate = True
autosummary_generate_overwrite = False
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}
autodoc_mock_imports = [
    'pandas',
    'numpy',
    'obspy',
    'tensorflow',
    'pygmt',
    'geopandas',
    'shapely',
    'matplotlib',
    'seaborn',
    'tqdm',
]

ROOT_DIR = Path(__file__).resolve().parents[3]
CODEBASE_FONTE = ROOT_DIR / '.specs' / 'codebase' / 'fonte'
for path in [
    CODEBASE_FONTE,
    CODEBASE_FONTE / 'nucleo',
    CODEBASE_FONTE / 'analise_dados',
    CODEBASE_FONTE / 'rnc',
]:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

extlinks = {
    'ghblob': (
        'https://github.com/Gabriel-Goes/Sismologia_IPT/blob/main/%s',
        '%s',
    ),
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_baseurl = os.environ.get('SPHINX_HTML_BASEURL', '')
