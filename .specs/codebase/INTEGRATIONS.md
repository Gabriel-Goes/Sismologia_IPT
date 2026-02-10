# External Integrations

**Analyzed from code/config references only (no live endpoint checks).**

## Seismological Data Services (FDSN)

### Primary acquisition service (USP internal endpoint)

- **Service:** FDSN endpoint at `http://10.110.1.132:18003`
- **Purpose:** Event metadata and waveform retrieval during main acquisition flow.
- **Location in code:** `fonte/nucleo/fluxo_eventos.py`
- **Authentication:** Not explicit in this client initialization.
- **Usage:** `Client(...).get_events(...)` and `get_waveforms(...)`.

### Backup acquisition service (RSBR)

- **Service:** `http://rsbr.on.br:8081`
- **Purpose:** Fallback source when primary query fails.
- **Location in code:** `fonte/nucleo/fluxo_eventos.py`
- **Authentication:** Not explicit.

### Additional/legacy FDSN endpoints

- **Service:** `http://seisarc.sismo.iag.usp.br`
  - **Location:** `fonte/nucleo/iag/getEventData.py`
- **Service:** `http://localhost:8091`
  - **Location:** `fonte/relatorio-sismologia/pyscripts/make_xml.py`
- **Service:** `http://10.100.0.150:8080` (with user/password)
  - **Location:** `fonte/analise_dados/testa_filtros.py`

## GIS and Mapping Integrations

### QGIS Desktop Plugin Runtime

- **Purpose:** Interactive event/pick visualization and map layer handling.
- **Location:** `fonte/interface/farejadorsismo/*`
- **Integration type:** In-process QGIS plugin (`qgis.core`, `qgis.PyQt` APIs).
- **Config references:**
  - `metadata.txt` (`qgisMinimumVersion=3.0`)
  - `pb_tool.cfg`
  - `Makefile`

### Local geospatial data files

- **Purpose:** Geographical filtering and rendering.
- **Files:**
  - `arquivos/figuras/mapas/shp/ne_110m_admin_0_countries.shp`
  - `arquivos/figuras/mapas/macrorregioesBrasil.json`
- **Used by:** `pre_processa.py`, `gera_mapas.py`.

## Waveform Inspection Tool

### Snuffler (Pyrocko ecosystem)

- **Purpose:** Manual inspection of waveform files.
- **Location:** `fonte/interface/farejador.py`, `fonte/interface/farejadorsismo/farejadorsismo_dockwidget.py`
- **Integration method:** `subprocess.Popen([...snuffler..., mseed_file_path])`

## Document / Report Toolchain

### LaTeX / pdfTeX

- **Purpose:** Final report generation from TeX templates and generated fragments.
- **Location:**
  - Orchestration: `fluxo_sismo.sh`
  - Content generators: `fonte/relatorio-sismologia/pyscripts/*`
- **Integration method:** local command execution (`pdflatex`).

## ML Model Artifact Integration

### TensorFlow Keras model

- **Artifact:** `fonte/rnc/model/model_2021354T1554.h5`
- **Purpose:** Event/pick classification.
- **Location:** loaded in `fonte/rnc/prediction.py`.
- **Interface:** local file load via `tf.keras.models.load_model(...)`.

## Environment and Packaging Integrations

### pyenv / pyenv-virtualenv

- **Purpose:** Local Python runtime setup.
- **Location:** `config/instalar.sh`
- **Method:** shell-driven install and environment activation.

### Docker CUDA image

- **Purpose:** Legacy compatibility with model stack and GPU runtime.
- **Location:** `config/dockerfile`
- **Base image:** `nvidia/cuda:11.8.0-base-ubuntu20.04`

### QGIS plugin distribution endpoint (optional tooling)

- **Service:** `plugins.qgis.org`
- **Location:** `fonte/interface/farejadorsismo/plugin_upload.py`
- **Purpose:** Upload packaged plugin (not part of core seismic pipeline execution).

## API / Webhook / Background Jobs

### API integrations

- Main external API style: FDSN HTTP clients (ObsPy client abstractions).
- No REST service implemented by this repository itself.

### Webhooks

- No webhook handlers found.

### Background jobs / queues

- No queue system or worker scheduler found.
- Execution is synchronous and script-driven.

