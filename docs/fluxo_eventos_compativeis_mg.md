# Fluxo MG Compativel (Step02 + Step03 + Organizacao)

Este fluxo gera dois conjuntos finais:
- `data/eventos_compativeis`: apenas eventos prontos para classificacao
- `data/eventos_nao_compativeis`: eventos fora dos criterios ou sem onda P utilizavel

## Descobertas do Notebook Step1 (RAW + ponto-poligono)
Fonte: `notebooks/step1_sisbra_selfcontained.ipynb` (execucao registrada no notebook).

- `rows_raw_total=5934`
- `rows_keep_in_mg=918`
- `rows_drop_outside_mg=4872`
- `rows_drop_no_valid_coords=144`
- `incons_st_mg_outside=15`
- `incons_st_not_mg_inside=13`
- `incons_st_empty_inside=0`

Conclusao:
- a pergunta "evento ocorreu em MG?" deve ser respondida por coordenadas
  (ponto-poligono), nao por `ST`/toponimia/localidade.
- `ST` deve ficar como trilha de auditoria para detectar inconsistencias do catalogo.

## Estado atual vs estado alvo
- Estado atual (scripts Python+Bash): gate de MG por ponto-poligono.
- `ST`/toponimia/localidade: somente auditoria de consistencia.
- Filtro de ano: aplicado por ultimo (`min-year`) nos scripts migrados.

## Execucao Real (target `data/events`)

Para a execucao operacional que para antes da rede neural, use:

```bash
cd /home/ggrl/projetos/ClassificadorSismologico
bash scripts/run_real_mg_maglt4_depthlt10.sh
```

No host `seisapp`, o wrapper detecta automaticamente o ambiente e usa
`CLIENT_URL=http://10.110.0.134` (sem precisar de tunel reverso).

No codigo atual, este wrapper aplica os criterios estritos:
- `match_status == matched`
- origem do evento dentro do poligono de MG
- `magnitude < 4`
- `depth_km < 10`
- `year >= 2020` (ultimo filtro)
- pick `P*` com `dist_km <= 400`
- janela `P-10s` a `P+50s`
- canais `HHZ,HHN,HHE`
- se duas linhas SISBRA casarem com o mesmo `fdsn.resource_id`, materializa
  um unico evento final com auditoria de duplicacao

Layout final:
- `data/events/YYYYJJJTHHMMSS/event.json`
- `data/events/YYYYJJJTHHMMSS/event.xml`
- `data/events/YYYYJJJTHHMMSS/waveform/NET_STA_DATETIME.mseed`

Layout de investigacao (nao-matched):
- `data/events_stage_non_matched/ambiguous/*/event.json`
- `data/events_stage_non_matched/no_match/*/event.json`
- `outputs/non_matched_audit.csv`
- `outputs/non_matched_audit.md`
- `outputs/ambiguous_events.csv`
- `outputs/no_match_events.csv`

Observacao:
- eventos `no_match`/`ambiguous` com agencia SISBRA contendo `IAG/USP` sao marcados como
  severidade `critical` na auditoria para investigacao prioritaria.
- o filtro de MG usa preferencialmente o GeoPackage local (`/home/gabrielgoes/geodatabase.gpkg`),
  sincronizado via `rsync` do GeoServer; `geobr` vira fallback.

Regra de seguranca:
- o wrapper aborta se `data/events` nao estiver vazio (nao faz limpeza automatica).
- precheck funcional de endpoint e feito com cliente `obspy` (nao usa `curl`).

## Criterios de Compatibilidade
- Implementado hoje (scripts):
  - `match_status == matched`
  - `inside_mg_polygon == True` (interseccao ponto-poligono)
  - `magnitude < 4`
  - `depth_km < 10`
  - `year >= min-year` (aplicado por ultimo)
  - existe pelo menos 1 pick `P*` com `dist_km <= 400`
  - forma de onda baixada em janela `P-10s` a `P+50s`
  - precisa haver pelo menos um conjunto 3C por estacao com canais: `HHZ`, `HHN`, `HHE`
- Auditoria:
  - `ST`/toponimia/localidade usados somente para comparacao com a geometria.

## Nomenclatura de Diretorio Final
- Em `eventos_compativeis`, o nome do diretorio e **somente**:
  - `YYYYMMDDTHHMMSS`
- Nao inclui `usp...`, `row...`, etc.
- Se houver colisao explicada pelo mesmo `fdsn.resource_id`, o pipeline faz
  merge do evento final e registra a duplicacao em `dedup` +
  `sisbra_duplicates`.
- Se houver colisao que **nao** possa ser explicada pelo mesmo
  `fdsn.resource_id`, o fluxo continua abortando com `datetime_collision`.

## Arquivos e Scripts
- Step02 (bundles): `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
- Step03 (ondas por pick P): `scripts/step03_waveforms_from_p_picks.py`
- Organizacao final: `scripts/organize_compatible_events.py`

Observacao:
- O Step02 grava no `event.json` o bloco `waveform_download_contract`
  (modo + canais + padrao de nome). O Step03 usa esse contrato automaticamente quando
  `--component-channels` nao e informado via CLI.
- Setup/check de ambiente pyenv: `docs/ambiente_pyenv.md`.
- Arquitetura e planejamento canonicos: `.specs/project/`, `.specs/codebase/` e `.specs/features/`.
- Scripts de diagnostico historico: `scripts/legacy/`.

## Execucao Recomendada
1. Normalizar o `RAW` em um CSV derivado proprio e separar linhas sem coordenadas validas:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/normalize_sisbra_raw.py \
  --input-csv catalogs/sisbra/sisbra_v2024May09/catalogo_RAW_v2024May09.csv \
  --output-csv outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalized_v2024May09.csv \
  --rejected-no-valid-coords-csv outputs/catalogs/sisbra_v2024May09/sisbra_raw_rejected_no_valid_coords_v2024May09.csv \
  --report-md outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalization_report_v2024May09.md
```

2. Gerar CSV filtrado por geometria MG/M<4/depth<10/ano a partir do derivado normalizado:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/filter_sisbra_csv.py \
  --input-csv outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalized_v2024May09.csv \
  --output-csv outputs/catalogs/sisbra_v2024May09/sisbra_raw_mg_maglt4_depthlt10_yearge2020_v2024May09.csv \
  --state MG \
  --mg-polygon-year 2020 \
  --mg-polygon-gpkg /home/gabrielgoes/geodatabase.gpkg \
  --mg-polygon-layer ibge_mg_uf_2024 \
  --max-mag 4 \
  --max-depth-km 10 \
  --min-year 2020
```
Observacao: `--state` e mantido apenas para auditoria de consistencia (`ST x geometria`).

3. Executar Step02 no subconjunto:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && LOG_DIR=outputs/logs_mg_maglt4_depthlt10_w24 WORKERS=24 N_LAST=0 OUT_ROOT=data/sisbra_mg_maglt4_depthlt10_w24 SISBRA_CSV=outputs/catalogs/sisbra_v2024May09/sisbra_raw_mg_maglt4_depthlt10_yearge2020_v2024May09.csv CLIENT_URL=http://127.0.0.1:28080 bash scripts/run_all_sisbra_build.sh
```

4. Baixar formas de onda (60 s = P-10 / P+50):
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/step03_waveforms_from_p_picks.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --client-url http://127.0.0.1:28080 --max-pick-dist-km 400 --pre-p-s 10 --post-p-s 50 --workers 12 --state-filter MG --mg-polygon-year 2020 --mg-polygon-gpkg /home/gabrielgoes/geodatabase.gpkg --mg-polygon-layer ibge_mg_uf_2024 --max-mag 4 --max-depth-km 10 --min-year 2020 --component-channels HHZ,HHN,HHE --summary-csv outputs/waveform_triplet_download_summary_mg.csv
```
- Com `--component-channels HHZ,HHN,HHE`, o default agora e salvar **1 arquivo 3C**
  por estacao no formato `NET_STA_DATETIME.mseed`.
- `DATETIME` usa origem do evento em UTC no formato juliano `%Y%jT%H%M%S`
  (ex.: `2022004T134407`).
- Para manter o modo legado (1 arquivo por canal), adicionar `--split-component-files`.

5. Organizar compativeis/incompativeis:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/organize_compatible_events.py --events-root data/sisbra_mg_maglt4_depthlt10_w24 --download-summary-csv outputs/waveform_triplet_download_summary_mg.csv --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --state-filter MG --mg-polygon-year 2020 --mg-polygon-gpkg /home/gabrielgoes/geodatabase.gpkg --mg-polygon-layer ibge_mg_uf_2024 --max-mag 4 --max-depth-km 10 --min-year 2020 --max-pick-dist-km 400 --report-csv outputs/eventos_compatibilidade_report.csv --report-md outputs/eventos_compatibilidade_report.md
```

5. Enforce de triplet HHZ/HHN/HHE em `eventos_compativeis`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/enforce_triplet_channels.py --compatible-root data/eventos_compativeis --incompatible-root data/eventos_nao_compativeis --required-channels HHZ,HHN,HHE --report-csv outputs/eventos_triplet_filter_report.csv --report-md outputs/eventos_triplet_filter_report.md
```

6. Opcional: consolidar 3 arquivos (`HHZ/HHN/HHE`) em um unico `.mseed` 3C por estacao com nome `NET_STA_DATETIME.mseed`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/merge_triplet_waveforms.py --compatible-root data/eventos_compativeis --waveforms-subdir waveforms --merged-subdir waveforms_3c --required-channels HHZ,HHN,HHE --summary-csv outputs/waveforms_3c_merge_summary.csv
```

7. Rodar inferencia RNC e persistir resultado no `event.json`:
```bash
cd /home/ggrl/projetos/ClassificadorSismologico && pyenv exec python scripts/run_rnc_eventos_compativeis.py --compatible-root data/eventos_compativeis --model-path models/rnc/model_2021354T1554.h5 --workers 4 --skip-existing --summary-events-csv outputs/rnc_prediction_events.csv --summary-picks-csv outputs/rnc_prediction_picks.csv --summary-errors-csv outputs/rnc_prediction_errors.csv
```

## Auditoria
- Relatorio por evento: `outputs/eventos_compatibilidade_report.csv`
- Relatorio resumido: `outputs/eventos_compatibilidade_report.md`
- Auditoria de nao-matched (consolidado): `outputs/non_matched_audit.csv`
- Auditoria de nao-matched (resumo): `outputs/non_matched_audit.md`
- Lista dedicada de `ambiguous`: `outputs/ambiguous_events.csv`
- Lista dedicada de `no_match`: `outputs/no_match_events.csv`
- Relatorio de merge por duplicacao SISBRA->FDSN: `outputs/events_duplicate_merge_report.csv`
- Resumo de download por pick/canal: `outputs/waveform_triplet_download_summary_mg.csv`
- Relatorio de filtro por triplet: `outputs/eventos_triplet_filter_report.md`
- Resumo de consolidacao 3C (opcional): `outputs/waveforms_3c_merge_summary.csv`
- Predicao RNC por evento: `outputs/rnc_prediction_events.csv`
- Predicao RNC por pick: `outputs/rnc_prediction_picks.csv`
- Erros da etapa RNC: `outputs/rnc_prediction_errors.csv`
