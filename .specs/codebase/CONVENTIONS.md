# Code Conventions

## Naming Conventions

### Directory Names

- Bundle Step02: `YYYYMMDDTHHMMSS_<eventid>_rowNNN`
- Base final compativel: `YYYYMMDDTHHMMSS` (somente datetime)

### Waveform Files

- Legado split por canal:
  - `NET.STA.LOC.CHA_PICKTIME.mseed`
  - Ex.: `BL.BB19B.--.HHN_20231214T005239108754Z.mseed`
- Alvo triplet em arquivo unico:
  - `NET_STA_DATETIME.mseed`
  - `DATETIME` em UTC juliano `%Y%jT%H%M%S`

### Metadata Files

- `event.json`: payload principal por evento.
- `event.xml`: QuakeML do evento selecionado.

### Report Files

- Prefixo `outputs/` para CSV/MD de auditoria.
- Nome orientado a etapa:
  - `waveform_*_summary*.csv`
  - `eventos_*_report*.{csv,md}`
  - `rnc_prediction_*.csv`

## CLI and Script Conventions

- Estilo CLI: `argparse` com defaults declarados no script.
- Wrappers bash usam env vars para parametrizacao sem editar codigo.
- Fallback de interpretador no shell: `pyenv exec python` -> `python3` -> `python`.

## Data Contract Conventions

- Step02 escreve `waveform_download_contract` em `event.json`.
- Step03 consome esse contrato quando `--component-channels` nao e informado.
- Campo `match_status` e chave de gate para organizacao.

### Future Contracts (planned)

- Catalog adapter canonico deve usar campos em snake_case:
  - `event_id`, `origin_time_utc`, `latitude`, `longitude`, `depth_km`, `magnitude`, `source_name`.
- Enriquecimento ANM deve ser aninhado em `event.json` sob:
  - `mining_context.nearest_distance_km`
  - `mining_context.has_active_mine_nearby`
  - `mining_context.source_version`

### External Baseline Mapping Rules (catalogo -> canonico)

- `origin_time_utc`:
  - preferir campo nativo UTC quando existir;
  - fallback: `data + "T" + hora_utc + "Z"`.
- `depth_km`:
  - usar valor da fonte quando existir;
  - manter `null` quando a fonte nao fornecer profundidade.
- `event_id`:
  - usar `event_id` da fonte quando existir;
  - fallback para UID deterministico (tempo + lat/lon + origem).
- `source_name`:
  - preencher explicitamente (`labsis_html`, `iag_fdsn`, `unb_fdsn`).
- `state_uf`:
  - manter como campo auxiliar de auditoria; criterio geografico principal segue
    coordenada + geometria.

## Status/Errors Conventions

- Status por etapa (exemplos):
  - download: `downloaded`, `skipped_exists`, `error`
  - organizacao: `compatible`/`incompatible` via `target_group`
  - triplet gate: `keep_compatible`, `move_to_incompatible`
  - inferencia: `ok`, `partial`, `no_valid_pick`, `error`, `skipped_existing`
- Erros sao serializados em CSV com contexto minimo (`event_id`, `scope`, `kind`, `message`).

## Known Variants (Documented, not hidden)

- Base atual contem coexistencia de outputs legados e novos.
- Adapter RNC aceita ambos os formatos de nome (`dotted` e `simple`).

## Evidence (arquivo:linha)

- Naming final compativel: `scripts/organize_compatible_events.py:14`
- Nome legado split: `scripts/step03_waveforms_from_p_picks.py:305`
- Nome alvo simple: `scripts/step03_waveforms_from_p_picks.py:245`
- Contrato no `event.json`: `src/seismic_event_discriminator/step02_fdsn_picks_export.py:234`
- Consumo do contrato no Step03: `scripts/step03_waveforms_from_p_picks.py:590`
- Adapter dual-format: `src/seismic_event_discriminator/rnc_adapter.py:12`, `src/seismic_event_discriminator/rnc_adapter.py:15`
- Fallback de interpretador em wrapper: `scripts/run_all_sisbra_build.sh:30`

## Update In 5 Minutes

1. Validar se naming do Step03 mudou.
2. Validar se schema de `event.json` (contrato) mudou.
3. Validar novos status de erro nos CSVs.
4. Atualizar apenas as secoes afetadas.
