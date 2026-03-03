# Testing Infrastructure

## Current Reality

- Nao existe suite unica de `pytest` cobrindo o pipeline inteiro.
- Validacao operacional atual e baseada em:
  - wrappers de lote/smoke
  - CSVs de resumo por etapa
  - relatorios `.md` de execucao

## Test Types in Use

### 1) Connectivity/Environment Smoke

- Verifica interpretador, `obspy` e endpoint FDSN.
- Principal script: `scripts/run_all_sisbra_build.sh`.

### 2) Step02 Batch Validation

- Entrada: SISBRA filtrado.
- Saida validada:
  - quantidade de bundles `event.json`
  - contagem `matched/no_match/ambiguous`
  - resumo CSV do lote.

### 3) Step03 Download Validation

- Valida filtros `P*`, janela de tempo e escrita de `.mseed`.
- Resultado em CSV com status por tarefa.

### 4) Compatibility Validation

- `organize_compatible_events.py`: aplica regras de negocio.
- `enforce_triplet_channels.py`: garante ao menos um triplet 3C.

### 5) RNC Inference Validation

- `run_rnc_eventos_compativeis.py` com:
  - `--limit-events`
  - `--sample-random --seed 42`
  - `--dry-run` (quando aplicavel)
- Verifica persistencia em `event.json` e 3 CSVs de auditoria.

## Suggested Repeatable Scenarios

## S1 - Step02 smoke curto

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
WORKERS=4 N_LAST=10 OUT_ROOT=data/sisbra_smoke CLIENT_URL=http://127.0.0.1:28080 bash scripts/run_all_sisbra_build.sh
```

Aceite:
- comando retorna `rc=0`
- existe `run_all_sisbra_<UTC>.md` com contagem de status
- existem `event.json` no `OUT_ROOT`

## S2 - Step03 dry-run estrutural

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
pyenv exec python scripts/step03_waveforms_from_p_picks.py \
  --events-root data/sisbra_mg_maglt4_depthlt10_w24 \
  --client-url http://127.0.0.1:28080 \
  --component-channels HHZ,HHN,HHE \
  --dry-run \
  --summary-csv outputs/waveform_triplet_download_summary_dryrun.csv
```

Aceite:
- CSV existe e tem colunas de status.
- `status` contem `planned`/`skipped_exists`/`error_*` coerentes.

## S3 - Organizacao + Enforce dry-run

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
pyenv exec python scripts/organize_compatible_events.py --dry-run
pyenv exec python scripts/enforce_triplet_channels.py --dry-run
```

Aceite:
- relatarios CSV/MD gerados sem mover arquivos.

## S4 - RNC amostra deterministica

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
PYENV_VERSION=geo-seis-rnc pyenv exec python scripts/run_rnc_eventos_compativeis.py \
  --compatible-root data/eventos_compativeis \
  --model-path models/rnc/model_2021354T1554.h5 \
  --limit-events 20 \
  --sample-random \
  --seed 42 \
  --workers 4 \
  --summary-events-csv outputs/rnc_prediction_events_smoke.csv \
  --summary-picks-csv outputs/rnc_prediction_picks_smoke.csv \
  --summary-errors-csv outputs/rnc_prediction_errors_smoke.csv
```

Aceite:
- 3 CSVs de saida gerados
- cada `event_id` possui status valido (`ok|partial|no_valid_pick|error|skipped_existing`)

## S5 - Drift check (obrigatorio apos refactor)

Checks:

1. Timestamp scripts vs outputs:
   - `scripts/step03_waveforms_from_p_picks.py`
   - `outputs/waveform_triplet_download_summary_mg.csv`
2. Header do CSV coerente com campos escritos no script.
3. `event.json` novo contem `waveform_download_contract`.

Aceite:
- divergencias documentadas no handoff/STATE quando existir mismatch.

## S6 - Catalog adapters parity (future)

Checks:

1. Adapter FDSN e adapter HTML produzem o mesmo schema canonico.
2. Campos obrigatorios (`origin_time_utc`, `latitude`, `longitude`, `magnitude`) estao presentes.
3. Dedupe por `event_id`/uid nao gera explosao de duplicatas.

Aceite:
- arquivo canonico de entrada do Step02 passa na validacao de schema.

## S7 - Contexto minerario ANM (future)

Checks:

1. Evento em area proxima de mina recebe `mining_context.has_active_mine_nearby=true`.
2. Evento distante recebe `false` ou distancia acima do limiar.
3. Campo de versao de fonte (`source_version`) e preenchido.

Aceite:
- `event.json` enriquecido e CSV de auditoria espacial coerente.

## S8 - STAC QA opcional (future)

Checks:

1. Falha no STAC nao interrompe pipeline principal.
2. Casos com baixa confianca geram artefato de QA separado.

Aceite:
- execucao principal finaliza mesmo com QA indisponivel.

## Current Gaps

- Sem testes unitarios formais para funcoes de parsing/naming.
- Sem validacao automatica de schema de `event.json`.
- Sem job CI para smoke minimo do pipeline.
- Sem suite dedicada para adapters multi-fonte (FDSN + HTML).
- Sem testes automatizados de join espacial com ANM.

## Evidence (arquivo:linha)

- Wrapper de lote e checks: `scripts/run_all_sisbra_build.sh:97`
- Smoke paralelo: `scripts/run_parallel_smoketest_seisapp.sh:4`
- Step03 status e CSV fields: `scripts/step03_waveforms_from_p_picks.py:715`
- Organize criterios: `scripts/organize_compatible_events.py:123`
- Enforce triplet: `scripts/enforce_triplet_channels.py:90`
- RNC seed e amostragem: `scripts/run_rnc_eventos_compativeis.py:393`, `scripts/run_rnc_eventos_compativeis.py:421`

## Update In 5 Minutes

1. Atualizar apenas comandos de smoke usados na ultima iteracao.
2. Registrar novos arquivos de resumo/relatorio.
3. Revisar apenas o bloco "Current Gaps" se mudou cobertura automatica.
