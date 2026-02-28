# Architecture

**Pattern:** Pipeline modular orientado a scripts (CLI), com persistencia em filesystem.

## High-Level Structure

```text
SISBRA CSV
  -> Step02 (match FDSN + picks + contrato de download)
  -> Step03 (download waveform, split ou triplet single-file)
  -> Organize compatible/incompatible
  -> Enforce triplet HHZ/HHN/HHE
  -> (Opcional) Merge split->3C
  -> RNC inference (atualiza event.json + CSVs)
```

## Critical Flow: Arquivo `.mseed` de exemplo

Exemplo atual (legado por canal):
`data/eventos_compativeis/20231214T005219/waveforms/BL.BB19B.--.HHN_20231214T005239108754Z.mseed`

Fluxo causal:

1. Step02 gera bundle do evento com picks e metadados (`event.json`, `event.xml`).
2. Step03 seleciona pick `P*` e baixa janela `P-10s/P+50s`.
3. Step03 grava arquivo `.mseed` por canal no formato legado quando o run esta em modo split (ou dados vieram de run legado).
4. Organizacao move evento para `eventos_compativeis/<DATETIME>/`.

## Modules and Responsibilities

### Step02: Match + Bundle

- Entrada: CSV SISBRA.
- Integracao: FDSN (events + stations).
- Saida: pasta por evento com `event.json` + `event.xml`.
- Contrato para Step03 embutido em `event.json` via `waveform_download_contract`.

### Step03: Waveform Download

- Entrada: bundles Step02.
- Selecao: picks P dentro de distancia.
- Modos:
  - split por canal (`NET.STA.LOC.CHA_PICKTIME.mseed`)
  - single-file 3C (`NET_STA_DATETIME.mseed`)
- Saida: CSV de resumo do download.

### Compatibility Gate

- `organize_compatible_events.py` aplica regras de negocio (estado, mag, profundidade, pick P valido, waveform existente).
- `enforce_triplet_channels.py` garante ao menos um triplet 3C por evento.

### RNC

- `run_rnc_eventos_compativeis.py` descobre triplets (legado e novo), executa inferencia e persiste `rnc_prediction` no `event.json`.
- Saidas de auditoria em 3 CSVs (`events`, `picks`, `errors`).

## Data Flow by Artifact

- `data/sisbra_*/*/event.json`: contrato e metadados por evento.
- `data/*/waveforms/*.mseed`: sinais para classificacao.
- `outputs/waveform_*_summary*.csv`: auditoria de download.
- `outputs/eventos_*_report*.{csv,md}`: auditoria de compatibilidade.
- `outputs/rnc_prediction_*.csv`: auditoria de inferencia.

## Drift Detection (Codigo x Artefatos)

Observacao operacional relevante:

- Scripts atuais foram atualizados depois de parte dos artefatos de `outputs/`.
- Evidencia temporal:
  - `outputs/waveform_triplet_download_summary_mg.csv` em `2026-02-27 18:24`
  - `scripts/step03_waveforms_from_p_picks.py` em `2026-02-27 20:14`
- Evidencia estrutural:
  - Header de `outputs/waveform_triplet_download_summary_mg.csv` nao inclui `event_datetime_tag`/`filename_pattern`, embora o script atual escreva esses campos.

Implicacao:
- Reproducao de bugs/mudancas deve sempre registrar `timestamp + commit + comando`.

## Boundaries

- Dominio: fluxo sismologico de preparo e classificacao.
- Infra: filesystem local e endpoints FDSN; sem banco transacional.
- Acoplamento principal:
  - Step03 depende da estrutura de `event.json` do Step02.
  - RNC depende de naming e consistencia 3C das formas de onda.

## Evidence (arquivo:linha)

- Contrato Step03 no Step02: `src/seismic_event_discriminator/step02_fdsn_picks_export.py:234`
- Modos Step03: `scripts/step03_waveforms_from_p_picks.py:526`, `scripts/step03_waveforms_from_p_picks.py:532`
- Nome alvo `NET_STA_DATETIME`: `scripts/step03_waveforms_from_p_picks.py:245`
- Nome legado split por canal: `scripts/step03_waveforms_from_p_picks.py:305`
- Organizacao compatibilidade: `scripts/organize_compatible_events.py:123`
- Enforce triplet: `scripts/enforce_triplet_channels.py:90`
- Merge opcional: `scripts/merge_triplet_waveforms.py:163`
- Adapter legado/novo: `src/seismic_event_discriminator/rnc_adapter.py:70`
- RNC persistindo em `event.json`: `scripts/run_rnc_eventos_compativeis.py:352`

## Update In 5 Minutes

1. Conferir se houve mudanca em Step02/Step03 (`event.json` contrato e naming).
2. Conferir se houve mudanca nos gates (`organize`/`enforce`).
3. Conferir se houve mudanca em integracao RNC (`adapter` + `run_rnc`).
4. Atualizar somente os blocos afetados acima.

