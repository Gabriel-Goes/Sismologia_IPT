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

## Planned Integrations (Future)

### ANM Mining Vectors

**Service:** ANM SIGMINE dados abertos  
**Status:** planned (M5)  
**Purpose:** enriquecer eventos com contexto minerario e proximidade de minas.  
**Implementation target:** modulo de enriquecimento espacial antes da analise final.  
**Expected artifact:** campo `mining_context` no `event.json` + CSV de auditoria.

### Additional Catalog Sources

**Services:** Labsis boletins (HTML), IAG FDSN, UnB FDSN  
**Status:** planned  
**Purpose:** ampliar cobertura de eventos com camada de adapters por fonte.  
**Implementation target:** camada unificada de ingestao que exporta CSV canonico para Step02.

### STAC Imagery for QA

**Service:** INPE BDC STAC  
**Status:** planned (optional)  
**Purpose:** fornecer evidencia visual para revisao de casos ambiguos da classificacao.  
**Implementation target:** pipeline opcional de QA, sem dependencia hard no fluxo principal.

## Compatibility Assessment With External Baselines (2026-03-03)

Sources avaliadas:
- `/home/ggrl/projetos/ipt/SISMO/catalogo/.specs/codebase/*`
- `/home/ggrl/projetos/ipt/SISMO/QA_SISMO/vetor_minerario/.specs/codebase/*`

Status por trilha:

1. Catalog adapters (Labsis/IAG/UnB): **compatible with mapping**
- Reuso direto de padroes de coleta, dedupe e persistencia de bruto.
- Ajuste necessario: mapeamento explicito para schema canonico (`origin_time_utc`, `depth_km`, `source_name`).

2. Contexto minerario ANM: **compatible**
- Reuso direto do fluxo ANM `zip -> shp -> gpkg` e padroes de auditoria espacial.
- Ajuste necessario: parametrizar UFs e evitar hardcode de estados fixos na implementacao futura.

3. STAC para QA: **compatible as optional module**
- Reuso de busca STAC + corte por AOI + fluxos de validacao visual.
- Restricao: permanecer desacoplado do caminho critico Step02->Step03->RNC.

4. Endpoint UnB: **needs normalization**
- Baseline `catalogo_novo.py` documenta default `164.41.28.154:5831`.
- Wrapper atual de health-check no Classificador usa `164.41.28.122:5831`.
- Regra alvo: endpoint sempre parametrizado por env/flag; sem host fixo em docs operacionais.

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

5. Adapter de catalogo retorna schema inconsistente:
- sinal: colunas obrigatorias ausentes no CSV canonico
- local: validacao de schema no pre-Step02

6. Enriquecimento ANM sem cobertura espacial:
- sinal: `mining_context` vazio/indeterminado
- local: CSV de auditoria espacial

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
