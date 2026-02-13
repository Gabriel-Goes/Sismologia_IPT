import os
import importlib

project = "Seismic Event Discriminator"
author = "Gabriel Goes"
release = "0.1.0"

extensions = [
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
]

# Optional extensions: keep docs buildable even when they are not installed
# (e.g. on fresh systems without pip installs yet).
_OPTIONAL_EXTS = [
    ("myst_parser", "myst_parser"),
    ("sphinx_copybutton", "sphinx_copybutton"),
    ("sphinx_design", "sphinx_design"),
]
for _ext, _mod in _OPTIONAL_EXTS:
    try:
        importlib.import_module(_mod)
    except Exception:
        continue
    extensions.append(_ext)

templates_path = ["_templates"]
exclude_patterns: list[str] = []

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

extlinks = {
    # Keep links stable without hardcoding raw URLs everywhere.
    "gh": ("https://github.com/Gabriel-Goes/Sismologia_IPT/%s", "%s"),
}

html_theme = "alabaster"
html_static_path = ["_static"]

html_theme_options = {
    # Sidebar quick access. "Legado" is built as a static sub-site under /legado/.
    "extra_nav_links": {
        "Legado (snapshot)": "legado/index.html",
        "Repositorio (GitHub)": "https://github.com/Gabriel-Goes/Sismologia_IPT",
    },
}

html_baseurl = os.environ.get("SPHINX_HTML_BASEURL", "")
