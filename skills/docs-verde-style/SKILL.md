---
name: docs-verde-style
description: Apply a Verde-like Sphinx documentation pattern where User Guide links to API objects, API pages link bidirectionally with source code via [source] and _modules pages, and Python code is documented in API (not in Artefatos). Use when editing docs/sphinx content for navigation, API/source linking, and documentation structure.
---

# Docs Verde Style

## Goal

Keep documentation in a Verde-like navigation model:

- User Guide -> API object docs
- API object docs -> `[source]` -> `_modules/...`
- Source pages -> `[docs]` back to API object docs

## Rules

1. Python code belongs to `API Reference`, not `Artefatos`.
2. `Artefatos` is reserved for non-Python files (Bash/TXT/TEX/CSV/etc).
3. In narrative pages (`visao_geral`, `guia/*`), object mentions must link to internal docs pages.
4. When needed, source links should point to `/_modules/...` pages on GitHub Pages, never as file downloads.
5. Keep ordering consistent with project convention:
- Trilha 1 = Legado
- Trilha 2 = Refatoracao

## Workflow

1. Inspect links in `docs/sphinx/source/visao_geral.rst` and `docs/sphinx/source/guia/*.rst`.
2. Ensure Python scripts/functions referenced there have API pages in `docs/sphinx/source/api/`.
3. Ensure `_modules` pages are generated for referenced Python objects (via autodoc/autosummary + viewcode).
4. Move any Python entry mistakenly listed in `docs/sphinx/source/artefatos/index.rst` back to API references.
5. Run Sphinx build and verify navigation end-to-end.

## Validation checklist

- `User Guide` links resolve to API pages.
- API pages show object signatures and `[source]` links.
- Source links land on `_modules` pages.
- No Python script appears in `Artefatos` toctree.
- Build succeeds with no broken references.
