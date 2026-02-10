# Tech Stack

**Analyzed:** 2026-02-10  
**Branch:** `ipt`  
**Commit:** `9c3c01be31b67e7711d9a46ce762782d629e2ea6`

## Core

- Language: Python (headers indicate Python 3.11.x in main scripts; Docker path for legacy model uses Python 3.7.9)
- Runtime: Bash + Python CLI scripts
- Packaging: `setuptools` (`setup.py`, `fonte/interface/setup.py`)
- Package manager: `pip` + `pyenv`/`pyenv-virtualenv` (`config/instalar.sh`)
- Project package:
  - `ClassificadorSismologico` version `0.4.0` (`setup.py`)
  - `FarejadorSismologico` version `0.1.0` (`fonte/interface/setup.py`)

## Data Science / Seismology

- `pandas`
- `numpy`
- `obspy`
- `tensorflow` / `keras` (model load and inference in `fonte/rnc/prediction.py`)
- `seaborn`
- `matplotlib`
- `tqdm`

## Geospatial

- `geopandas`
- `shapely`
- `pygmt`
- Local GIS assets:
  - `arquivos/figuras/mapas/shp/ne_110m_admin_0_countries.shp`
  - `arquivos/figuras/mapas/macrorregioesBrasil.json`

## Desktop / GUI

- `PyQt5` (standalone viewer in `fonte/interface/farejador.py`)
- QGIS Plugin API (`qgis.*`) in `fonte/interface/farejadorsismo/*`
- QGIS plugin metadata:
  - `qgisMinimumVersion=3.0` (`fonte/interface/farejadorsismo/metadata.txt`)

## Reporting / Document Generation

- `pdflatex` invoked by `fluxo_sismo.sh`
- LaTeX scripts and templates under `fonte/relatorio-sismologia/`
- CSV -> TeX conversion scripts (for example `tabela.py`, `tabela_tex.py`)

## External Services

- FDSN seismic services:
  - `http://10.110.1.132:18003` (`fonte/nucleo/fluxo_eventos.py`)
  - `http://rsbr.on.br:8081` (`fonte/nucleo/fluxo_eventos.py`)
  - `http://seisarc.sismo.iag.usp.br` (`fonte/nucleo/iag/getEventData.py`)
  - `http://localhost:8091` (`fonte/relatorio-sismologia/pyscripts/make_xml.py`)
  - `http://10.100.0.150:8080` (`fonte/analise_dados/testa_filtros.py`)

## Container / Reproducible Legacy Runtime

- `config/dockerfile` based on `nvidia/cuda:11.8.0-base-ubuntu20.04`
- Pins legacy stack for original model compatibility:
  - `python 3.7.9`
  - `tensorflow==2.8.0`
  - `obspy==1.2.2`
  - `numpy==1.21.3`
  - `pandas==1.2.0`

## Development Tools

- Shell scripts: `fluxo_sismo.sh`, `plugin.sh`, `farejador.sh`, `config/instalar.sh`
- QGIS plugin toolchain:
  - `pyrcc5`
  - `nosetests`
  - `pylint`
  - `pep8`
  - `make` targets in `fonte/interface/farejadorsismo/Makefile`
- Documentation tooling:
  - Sphinx files under `fonte/interface/farejadorsismo/help/`

