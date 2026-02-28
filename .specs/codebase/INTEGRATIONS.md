# External Integrations

## FDSN Service (Primary)

**Service:** seisArc FDSNWS  
**Purpose:** buscar eventos, picks e waveforms para Step02/Step03.  
**Implementation:** ObsPy `Client` em Step02 e Step03.  
**Configuration:** `--client-url` (default local/tunel ou host direto).  
**Authentication:** sem credenciais no fluxo atual (HTTP endpoint).

## FDSN Service (Secondary Health Check)

**Service:** UnB endpoint (`164.41.28.122:5831`)  
**Purpose:** diagnostico de conectividade no wrapper de lote.  
**Implementation:** `curl` no `run_all_sisbra_build.sh`.  
**Observation:** pode falhar por timeout de rede/firewall sem quebrar o fluxo principal.

## Filesystem Integration

**Purpose:** todo estado de pipeline e auditoria e baseado em arquivos locais.

Paths chave:

- Entrada:
  - `catalogs/sisbra/...csv`
- Processamento:
  - `data/sisbra_*/*/event.{json,xml}`
  - `data/eventos_compativeis/*/waveforms/*.mseed`
- Auditoria:
  - `outputs/*.csv`
  - `outputs/logs*/run_all_sisbra_*.{log,md,csv}`

## Model Integration (RNC)

**Model file:** `models/rnc/model_2021354T1554.h5`  
**Purpose:** inferencia Natural vs Anthropogenic por pick/evento.  
**Implementation:** `scripts/run_rnc_eventos_compativeis.py` + `src/.../rnc_infer.py`.  
**Contract:** injeta bloco `rnc_prediction` no `event.json` e gera CSVs.

## Naming Compatibility Integration

**Problem:** coexistencia de nomenclaturas legado e nova para `.mseed`.  
**Implementation:** `rnc_adapter` suporta:

- legado: `NET.STA.LOC.CHA_PICKTIME.mseed`
- novo: `NET_STA_DATETIME.mseed`

**Impact:** permite transicao gradual sem quebrar inferencia.

## Environment Integration

**GeoServer:**
- `pyenv` com ambiente local `geo-seis`.
- Para TensorFlow, ambiente dedicado `geo-seis-rnc`.

**SEISAPP:**
- execucao direta com `python3` quando `pyenv` nao existe.

## Failure Modes and Signals

1. Endpoint FDSN indisponivel:
- sinal: `FDSNNoServiceException` / `curl` fail
- local: relatorio `run_all_sisbra_*.md`

2. Metadata de estacao ausente:
- sinal: pick em `picks_skipped` com `no_station_metadata`
- local: `event.json`

3. Triplet incompleto:
- sinal: `incomplete_triplet` no adapter / `move_to_incompatible` no gate
- local: CSV de erro e relatorio de filtro

4. Modelo ausente/incompativel:
- sinal: `model file not found` ou `error_preprocess/error_inference`
- local: stdout + `outputs/rnc_prediction_errors.csv`

## Evidence (arquivo:linha)

- Step02 FDSN client: `src/seismic_event_discriminator/step02_fdsn_picks_export.py:459`
- Step03 waveform client: `scripts/step03_waveforms_from_p_picks.py:401`
- Check seisArc/UnB no wrapper: `scripts/run_all_sisbra_build.sh:99`, `scripts/run_all_sisbra_build.sh:107`
- Modelo RNC default: `scripts/run_rnc_eventos_compativeis.py:30`
- Persistencia `rnc_prediction`: `scripts/run_rnc_eventos_compativeis.py:353`
- Compatibilidade de naming: `src/seismic_event_discriminator/rnc_adapter.py:12`, `src/seismic_event_discriminator/rnc_adapter.py:15`
- Guia de ambiente pyenv: `docs/ambiente_pyenv.md:7`, `docs/ambiente_pyenv.md:48`

## Update In 5 Minutes

1. Confirmar endpoints ativos e defaults de URL.
2. Confirmar caminho/versionamento do modelo.
3. Confirmar se novos erros de integracao surgiram nos CSVs/relatorios.
4. Atualizar somente os blocos alterados.

