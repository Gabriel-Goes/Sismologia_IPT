# Style Rules (Verde-like)

## Navigation

- User Guide references should point to API object pages (`/api/generated/...`).
- API pages should expose `[source]` links via Sphinx `viewcode`.
- Source pages under `_modules` should offer `[docs]` return links.

## Content placement

- Python: `docs/sphinx/source/api/`
- Non-Python: `docs/sphinx/source/artefatos/`

## Link policy

- Prefer internal Sphinx links (`:doc:`) for docs navigation.
- Use explicit `_modules/...` links only when direct source navigation is required.
- Avoid linking to downloadable raw files when the intent is code reading.

## Consistency

- Keep trilhos naming/order: `Trilha 1 = Legado`, `Trilha 2 = Refatoracao`.
