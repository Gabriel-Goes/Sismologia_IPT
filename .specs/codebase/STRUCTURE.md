# Project Structure

**Root:** `/home/ggrl/projetos/ClassificadorSismologico`

## Directory Tree (max 3 levels)

```text
.
├── .specs/
│   ├── project/
│   ├── features/
│   └── codebase/
├── src/
│   └── seismic_event_discriminator/
├── scripts/
│   └── dev/
├── docs/
│   ├── fluxo_eventos_compativeis_mg.md
│   └── ambiente_pyenv.md
├── data/
│   ├── sisbra_mg_maglt4_depthlt10_w24/
│   ├── eventos_compativeis/
│   └── eventos_nao_compativeis/
├── outputs/
│   ├── logs_mg_maglt4_depthlt10_w24/
│   └── *.csv / *.md
├── models/
│   └── rnc/
└── third_party/
    └── rnc_legacy/
```

## Planned Future Layout (not implemented yet)

```text
.
├── data/
│   └── geospatial/
│       ├── anm/
│       │   └── *.gpkg
│       └── mg_boundary/
├── src/seismic_event_discriminator/
│   ├── catalog_adapters/
│   │   ├── base.py
│   │   ├── fdsn_adapter.py
│   │   └── labsis_html_adapter.py
│   └── spatial_enrichment/
│       └── mining_context.py
└── scripts/
    ├── ingest_catalog_sources.py
    └── enrich_events_with_mining_context.py
```

## Module Organization

### Core Pipeline

- Location: `src/seismic_event_discriminator/` + `scripts/`
- Purpose: montar bundle de evento, baixar ondas, filtrar, classificar.
- Key files:
  - `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
  - `scripts/step03_waveforms_from_p_picks.py`
  - `scripts/organize_compatible_events.py`
  - `scripts/enforce_triplet_channels.py`

### Execution Wrappers

- Location: `scripts/run_*.sh`, `scripts/run_*.py`
- Purpose: comandos reprodutiveis para lote/smoke/diagnostico.
- Key files:
  - `scripts/run_all_sisbra_build.sh`
  - `scripts/run_parallel_smoketest_seisapp.sh`
  - `scripts/run_step02.sh`

### RNC Integration

- Location: `scripts/run_rnc_eventos_compativeis.py`, `src/seismic_event_discriminator/rnc_*`
- Purpose: inferencia e persistencia de predicao por evento.

### Documentation and Specs

- Location: `docs/` e `.specs/`
- Purpose:
  - `docs/`: runbooks operacionais.
  - `.specs/`: memoria de projeto e planejamento.

### Planned: Catalog Adapter Layer

- Location alvo: `src/seismic_event_discriminator/catalog_adapters/`
- Purpose: uniformizar multiplas fontes (FDSN + HTML) em um contrato canonico.

### Planned: Spatial Enrichment Layer (ANM)

- Location alvo: `src/seismic_event_discriminator/spatial_enrichment/`
- Purpose: calcular contexto minerario por evento.

## Where Things Live

**Associacao SISBRA->FDSN**
- Logic: `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
- Run wrapper: `scripts/run_all_sisbra_build.sh`
- Logs: `outputs/logs*/run_all_sisbra_*.{log,md,csv}`

**Download de Waveforms**
- Logic: `scripts/step03_waveforms_from_p_picks.py`
- Output: `data/*/waveforms/*.mseed`
- Summary: `outputs/waveform_*_summary*.csv`

**Compatibilidade de Eventos**
- Logic: `scripts/organize_compatible_events.py`
- Gates adicionais: `scripts/enforce_triplet_channels.py`
- Reports: `outputs/eventos_*_report*.{csv,md}`

**Inferencia RNC**
- Runner: `scripts/run_rnc_eventos_compativeis.py`
- Adapter: `src/seismic_event_discriminator/rnc_adapter.py`
- Model: `models/rnc/model_2021354T1554.h5`
- Reports: `outputs/rnc_prediction_*.csv`

## Priority Index (P0/P1/P2)

### P0 (sempre carregar primeiro)

1. `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
2. `scripts/step03_waveforms_from_p_picks.py`
3. `scripts/organize_compatible_events.py`
4. `outputs/waveform_triplet_download_summary_mg.csv`
5. `outputs/logs_mg_maglt4_depthlt10_w24/run_all_sisbra_20260227T211349Z.md`

### P1 (carregar quando for mexer no gate/inferencia)

1. `scripts/enforce_triplet_channels.py`
2. `scripts/merge_triplet_waveforms.py`
3. `scripts/run_rnc_eventos_compativeis.py`
4. `src/seismic_event_discriminator/rnc_adapter.py`

### P2 (contexto operacional/documental)

1. `README.md`
2. `docs/fluxo_eventos_compativeis_mg.md`
3. `docs/ambiente_pyenv.md`
4. `.specs/project/ROADMAP.md` (secoes M5 e futuras integracoes)

## Evidence (arquivo:linha)

- Estrategia de execucao wrapper: `scripts/run_all_sisbra_build.sh:141`
- Fluxo smoke paralelo: `scripts/run_parallel_smoketest_seisapp.sh:29`
- Fluxo operacional documentado: `docs/fluxo_eventos_compativeis_mg.md:22`
- Ambiente pyenv/fallback: `docs/ambiente_pyenv.md:7`, `docs/ambiente_pyenv.md:48`

## Update In 5 Minutes

1. Rodar `find . -maxdepth 2 -type d` para checar mudancas de topologia.
2. Validar lista P0/P1/P2 com base no ultimo run real.
3. Ajustar apenas os blocos de localizacao/ownership alterados.
