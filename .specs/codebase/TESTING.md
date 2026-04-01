# Testing

## Current Reality

- nao existe suite formal de `pytest` no repositorio
- a validacao principal e operacional
- o projeto verifica comportamento por:
  - wrappers de lote/smoke
  - CSVs de resumo
  - relatorios Markdown
  - notebooks de auditoria

## Test Types Observed

### Environment smoke

- `scripts/run_all_sisbra_build.sh` valida interpretador, `obspy` e conectividade com endpoints FDSN antes do lote.

### Step02 batch validation

- o proprio wrapper gera summary CSV e relatorio com contagem de `matched`, `ambiguous` e `no_match`.

### Step03 download validation

- `scripts/step03_waveforms_from_p_picks.py` produz CSV de status por tarefa de download.
- esse CSV e reutilizado pelo gate de compatibilidade.

### Compatibility validation

- `scripts/organize_compatible_events.py` gera CSV e Markdown de compatibilidade
- `scripts/enforce_triplet_channels.py` gera CSV e Markdown do filtro de triplet

### Inference validation

- `scripts/run_rnc_eventos_compativeis.py` gera:
  - `outputs/rnc_prediction_events.csv`
  - `outputs/rnc_prediction_picks.csv`
  - `outputs/rnc_prediction_errors.csv`
- a validacao e feita por status, contagem de erros e persistencia no `event.json`

## What Is Missing

- testes unitarios para parsing de filenames e contratos
- testes automatizados para schema de `event.json`
- fixtures pequenas e versionadas para smoke offline
- CI minima para verificar gates e compatibilidade de naming

## Recommended Repeatable Checks

### S1. Step02 smoke curto

- executar `scripts/run_all_sisbra_build.sh` com `N_LAST` pequeno e `OUT_ROOT` isolado
- verificar bundles `event.json` e summary CSV

### S2. Step03 dry-run ou amostra pequena

- executar `scripts/step03_waveforms_from_p_picks.py` contra poucos bundles
- verificar CSV de status e coerencia do naming final

### S3. Gates offline

- rodar `organize_compatible_events.py --dry-run`
- rodar `enforce_triplet_channels.py --dry-run`
- conferir reports sem mover arquivos

### S4. RNC amostral

- rodar `scripts/run_rnc_eventos_compativeis.py` com `--limit-events`, `--sample-random` e `--seed`
- verificar os tres CSVs e persistencia parcial no `event.json`

## Residual Risk

- sem fixtures pequenas, qualquer refactor depende de dados reais e ambiente operacional
- como parte do comportamento esta no filesystem, falhas podem aparecer so no fim do fluxo
