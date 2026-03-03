# Tech Stack

**Analyzed:** 2026-03-03  
**Scope:** Pipeline ativo (Step02 -> Step03 -> organizacao -> filtro triplet -> RNC).

## Core

- Language: Python 3 (execucao principal por scripts).
- Runtime strategy:
  - GeoServer: `pyenv exec python` com `.python-version=geo-seis`.
  - SEISAPP/fallback: `python3`/`python` quando `pyenv` nao existe.
- Package management:
  - Requisitos simples por arquivo txt (`scripts/dev/requirements-*.txt`).
  - Sem `pyproject.toml`/Poetry no fluxo atual.

## Main Libraries

- Pipeline core: `numpy`, `pandas`, `obspy`, `matplotlib`.
- Inferencia RNC: core + `tensorflow`.

## Candidate Libraries (Future Integration)

- Catalog adapters (instituicoes sem FDSN padrao):
  - `requests`
  - `beautifulsoup4`
- Geospatial contexto minerario (ANM):
  - `geopandas`
  - `shapely`
  - `rasterio` (apenas se houver analise raster)
- STAC imagery QA (opcional):
  - `pystac-client`

Observacao:
- Estas dependencias sao candidatas para implementacao futura e nao sao
  obrigatorias no fluxo Step02->Step03->RNC atual.

## Processing Model

- Step02:
  - Thread pool para consultas FDSN.
  - Exporta `event.json` + `event.xml` por evento.
- Step03:
  - Thread pool para download de formas de onda.
  - Suporta 2 formatos de output:
    - Legado por canal: `NET.STA.LOC.CHA_PICKTIME.mseed`
    - Alvo consolidado: `NET_STA_DATETIME.mseed`
- RNC:
  - `ProcessPoolExecutor` para inferencia paralela por evento.

## Data Formats

- Input catalog: CSV SISBRA filtrado.
- Event bundle: JSON + QuakeML XML.
- Waveform: MiniSEED (`.mseed`).
- Auditoria/relatorios: CSV + Markdown.

## External Services

- FDSN Event/Station/Waveform (seisArc via URL configuravel).
- Endpoint UnB apenas para cheque de conectividade no wrapper de lote.
- Nao ha dependencia de banco de dados no pipeline principal.

## Development Tools

- Bash wrappers para execucao reproducivel.
- `curl` para health checks de endpoint FDSN.
- `pyenv` com script de bootstrap (`scripts/dev/setup_pyenv_project.sh`).

## Evidence (arquivo:linha)

- `.python-version` com `geo-seis`: `.python-version`
- Fallback pyenv/python3/python: `scripts/run_all_sisbra_build.sh:30`, `scripts/run_all_sisbra_build.sh:34`, `scripts/run_all_sisbra_build.sh:37`
- Requisitos core: `scripts/dev/requirements-core-pipeline.txt:1`
- Requisitos RNC: `scripts/dev/requirements-rnc-inference.txt:1`
- Step02 export bundle + contrato Step03: `src/seismic_event_discriminator/step02_fdsn_picks_export.py:199`, `src/seismic_event_discriminator/step02_fdsn_picks_export.py:234`
- Step03 formatos e nome alvo: `scripts/step03_waveforms_from_p_picks.py:10`, `scripts/step03_waveforms_from_p_picks.py:245`, `scripts/step03_waveforms_from_p_picks.py:305`
- RNC process pool: `scripts/run_rnc_eventos_compativeis.py:487`

## Update In 5 Minutes

1. Verificar alteracoes em `scripts/dev/requirements-*.txt`.
2. Confirmar se `.python-version` mudou.
3. Conferir se Step03/RNC mudaram estrategia de concorrencia.
4. Atualizar apenas se algum item acima mudou.
