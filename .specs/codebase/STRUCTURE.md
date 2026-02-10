# Project Structure

**Root:** `/home/ggrl/projetos/ClassificadorSismologico`

## Directory Tree (max depth: 3)

```text
.
├── arquivos/
│   ├── catalogo/
│   ├── eventos/
│   ├── figuras/
│   ├── registros/
│   └── resultados/
├── config/
├── documentação/
├── fonte/
│   ├── analise_dados/
│   ├── interface/
│   │   └── farejadorsismo/
│   ├── nucleo/
│   │   └── iag/
│   ├── relatorio-sismologia/
│   │   ├── docs/
│   │   ├── pyscripts/
│   │   └── tex/
│   └── rnc/
├── fluxo_sismo.sh
├── farejador.sh
├── plugin.sh
└── setup.py
```

## Module Organization

### `fonte/analise_dados`

- **Purpose:** Pre and post-processing, statistics, plotting, mapping support.
- **Key files:**
  - `pre_processa.py` (catalog filtering and exploratory plots)
  - `pos_processa.py` (post-inference metrics and plots)
  - `gera_mapas.py` (map rendering)
  - `testa_filtros.py` (signal/noise filter experiments)

### `fonte/nucleo`

- **Purpose:** Seismic event acquisition and shared utilities.
- **Key files:**
  - `fluxo_eventos.py` (event metadata + waveform download)
  - `utils.py` (constants and shared helpers)
  - `iag/getEventData.py`, `iag/exporter.py` (auxiliary/legacy FDSN scripts)

### `fonte/rnc`

- **Purpose:** Neural pipeline (spectrogram extraction and classification).
- **Key files:**
  - `run.py` (inference entrypoint)
  - `data_process.py` (FFT/spectrogram generation)
  - `prediction.py` (model loading and prediction)
  - `model/model_2021354T1554.h5`

### `fonte/interface`

- **Purpose:** User-facing visualization.
- **Key files:**
  - `farejador.py` (standalone PyQt viewer)
  - `farejadorsismo/` (QGIS plugin, dock widget, resources, tests, plugin metadata)

### `fonte/relatorio-sismologia`

- **Purpose:** Report-generation stack (CSV -> TeX -> PDF).
- **Key areas:**
  - `pyscripts/` (automated table/figure/map TeX generation)
  - `tex/` (report templates and outputs by client/report type)
  - `docs/` (auxiliary LaTeX docs and examples)

## Where Things Live

**Acquisition and seismic raw data**

- Input catalogs: `arquivos/catalogo/`
- Downloaded waveforms: `arquivos/mseed/` (created at runtime by acquisition scripts)
- Acquisition outputs/errors: `arquivos/eventos/`

**Inference and model artifacts**

- Model file: `fonte/rnc/model/`
- Intermediate spectrograms: `arquivos/espectros/` (runtime output)
- Prediction outputs: `arquivos/resultados/predito.csv`

**Post-analysis and visualization**

- Processed datasets: `arquivos/resultados/`
- Figures: `arquivos/figuras/pre_processa/`, `arquivos/figuras/pos_processa/`, `arquivos/figuras/mapas/`
- GUI layers/inspection use same CSV contracts from `arquivos/resultados/`

**Reporting**

- Report scripts: `fonte/relatorio-sismologia/pyscripts/`
- TeX templates: `fonte/relatorio-sismologia/tex/`
- Final PDFs/logs: `arquivos/resultados/relatorios/` and report-specific `tex/*/logs/`

**Configuration / Environment**

- Python dependencies and install automation: `config/requirements.txt`, `config/instalar.sh`
- Legacy container environment: `config/dockerfile`
- QGIS plugin metadata/build config: `fonte/interface/farejadorsismo/metadata.txt`, `pb_tool.cfg`, `Makefile`

## Special Directories

### `arquivos/`

- Runtime data lake for the pipeline.
- Holds both source-like inputs and generated outputs.
- Important for reproducibility, but currently mixes transient and long-lived artifacts.

### `documentação/`

- Human-facing project documentation for refactoring and handoff.
- Current baseline docs exist before `.specs/` adoption.

### `.specs/` (newly introduced)

- Structured planning/mapping docs for spec-driven refactoring workflow.
- Current folder in this phase: `.specs/codebase/`.

