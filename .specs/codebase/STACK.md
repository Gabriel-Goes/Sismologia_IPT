# Tech Stack

**Analyzed:** 2026-03-31
**Scope:** codigo ativo em `src/`, `scripts/`, `docs/` e manifests locais.

## Core

- Language: Python 3.
- Runtime:
  - ambiente principal `geo-seis` via `.python-version`
  - ambiente dedicado `geo-seis-rnc` para inferencia com TensorFlow
- Package management:
  - manifests simples em `scripts/dev/requirements-core-pipeline.txt`
  - manifest complementar em `scripts/dev/requirements-rnc-inference.txt`
  - sem `pyproject.toml`, `setup.cfg` ou Poetry
- Shell tooling: Bash para wrappers operacionais e bootstrap de ambiente.

## Main Libraries

- Catalog/pipeline/data: `numpy`, `pandas`, `obspy`, `matplotlib`
- Geospatial gate: `geobr`, `geopandas`, `shapely`
- Inference: `tensorflow`
- Docs build: requirements separados em `docs/sphinx/requirements.txt`

## Execution Model

- Step01/Step02: scripts Python CLI com `argparse`
- Lote/smoke: wrappers `.sh` em `scripts/`
- Paralelismo:
  - `ThreadPoolExecutor` no match FDSN e download de waveforms
  - `ProcessPoolExecutor` na inferencia RNC

## Data Formats

- Input catalog: CSV SISBRA
- Match/export bundle: `event.json` + `event.xml`
- Waveforms: MiniSEED (`.mseed`)
- Reports/audit: CSV e Markdown
- Model artifact: `.h5`

## External Services

- FDSNWS via ObsPy `Client` para eventos, estacoes e waveforms
- seisArc como endpoint primario
- endpoint UnB apenas para health check em wrapper
- GeoPackage local ou `geobr` para o filtro geografico de MG

## Development Tools

- `pyenv` via `scripts/dev/setup_pyenv_project.sh`
- Sphinx em `docs/sphinx/`
- notebooks self-contained para analise e auditoria

## Notes

- O repo e script-first: a maior parte da orquestracao mora em `scripts/`.
- `third_party/rnc_legacy/` e baseline historico de referencia, nao a implementacao principal atual.
