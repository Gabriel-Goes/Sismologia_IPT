# Review da codebase - pipeline E2E MG mag<4 depth<10 (SISBRA -> picks -> waveforms)

## Escopo
Review do fluxo principal E2E que implementa:
- eventos SISBRA de MG
- magnitude < 4
- profundidade < 10 km
- picks P com distancia <= 400 km
- download de janela 60 s (P-10, P+50)
- triplet de canais HHZ/HHN/HHE
- alinhamento com as descobertas do notebook Step1 (filtro MG por geometria)

> Update 2026-03-02: migracao M1.1 implementada nos scripts principais.
> Este review permanece como registro dos gaps identificados antes da migracao.
> Update 2026-03-04: smoke E2E executado com endpoint interno SEISAPP e
> evidencia operacional registrada em `outputs/logs_real_events/`.
> Update 2026-03-06: `catalogo_RAW_v2024May09.csv` passa a ser a fonte canonica
> e o pipeline ganha uma etapa explicita de normalizacao propria antes do filtro MG.
> Update 2026-03-06: M1.2 foi rerodado com sucesso apos introduzir
> `merge_by_fdsn` no materialize; o caso `usp2021flcy` agora consolida duas
> linhas SISBRA em um unico evento final auditavel.

Arquivos revisados:
- scripts/run_real_mg_maglt4_depthlt10.sh
- scripts/filter_sisbra_csv.py
- src/seismic_event_discriminator/step02_fdsn_picks_export.py
- scripts/step03_waveforms_from_p_picks.py
- scripts/materialize_events_dataset.py

## Update 2026-03-04 (smoke controlado, seed=42 n=300)
Status dos gaps historicos deste review:
- S1 (gate MG por `ST`): **resolvido**. Gate atual usa ponto-poligono e `ST`
  fica apenas para auditoria (`scripts/filter_sisbra_csv.py`,
  `scripts/step03_waveforms_from_p_picks.py`, `scripts/materialize_events_dataset.py`).
- S2 (prioridade de datetime no Step03): **resolvido**.
  `fdsn.origin_time` agora e priorizado na tag `YYYYJJJTHHMMSS`
  (`scripts/step03_waveforms_from_p_picks.py`).
- S3 (defaults Step03 x materialize): **resolvido**.
  Ambos usam `waveform` e summary triplet por padrao.

Resumo do smoke:
- filtro: `rows_in=300`, `passed_geo_inside_mg=51`, `rows_out=14`
- Step02: `matched=14`, `no_match=0`, `ambiguous=0`, `error=0`
- Step03: `triplet_tasks=75`, `downloaded=58`, `error=17`
- materialize: `eligible=14`, `moved=14`
- erro predominante do Step03: `HTTP 204 No data available for request`
  (faltas de canal/estacao, sem bloquear elegibilidade dos eventos).

Artefatos:
- `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260304T121721Z.md`
- `outputs/smoke/waveform_triplet_download_summary_smoke.csv`
- `outputs/smoke/events_materialize_report_smoke.csv`

## Visao do fluxo implementado
1. Filtro SISBRA (state/year/mag/depth) em `filter_sisbra_csv.py`.
2. Match SISBRA->FDSN e export de `event.json`/`event.xml` + picks <= 400 km em `step02_fdsn_picks_export.py`.
3. Download de waveform no Step03 com fase P, janela P-10/P+50 e triplet por estacao em `step03_waveforms_from_p_picks.py`.
4. Materializacao final em `data/events` com checagem de elegibilidade em `materialize_events_dataset.py`.

## Matriz de conformidade requisito -> implementacao

### R1 - Gate geografico MG, mag < 4, depth < 10
Status: PARCIAL (scripts atuais usam `ST`; criterio alvo aprovado usa ponto-poligono)
- Filtro primario SISBRA no inicio:
  - `scripts/filter_sisbra_csv.py:58` (state default MG)
  - `scripts/filter_sisbra_csv.py:60` (max-mag default 4.0, estrito)
  - `scripts/filter_sisbra_csv.py:66` (max-depth default 10.0, estrito)
  - `scripts/filter_sisbra_csv.py:101`-`scripts/filter_sisbra_csv.py:123` (aplicacao dos filtros)
- Runner real usa esses filtros:
  - `scripts/run_real_mg_maglt4_depthlt10.sh:153`-`scripts/run_real_mg_maglt4_depthlt10.sh:159`
- Defesa em profundidade no Step03 e materialize:
  - `scripts/step03_waveforms_from_p_picks.py:562`-`scripts/step03_waveforms_from_p_picks.py:576`
  - `scripts/materialize_events_dataset.py:204`-`scripts/materialize_events_dataset.py:209`
- Divergencia com criterio alvo:
  - os gates atuais dependem de `ST` no filtro inicial, Step03 e materialize.
  - notebook Step1 mostrou casos inconsistentes `ST x geometria`.

### R2 - Picks a <= 400 km
Status: OK
- Step02 ja grava somente picks <= limite:
  - `src/seismic_event_discriminator/step02_fdsn_picks_export.py:177`-`src/seismic_event_discriminator/step02_fdsn_picks_export.py:193`
  - default `--max-pick-dist-km=400` em `src/seismic_event_discriminator/step02_fdsn_picks_export.py:435`
- Step03 refiltra por distancia:
  - `scripts/step03_waveforms_from_p_picks.py:140`-`scripts/step03_waveforms_from_p_picks.py:142`
- Materialize valida novamente para elegibilidade:
  - `scripts/materialize_events_dataset.py:176`-`scripts/materialize_events_dataset.py:183`

### R3 - Somente onda P (P*)
Status: OK
- Step03 usa `phase_hint` iniciando com `P`:
  - `scripts/step03_waveforms_from_p_picks.py:49`-`scripts/step03_waveforms_from_p_picks.py:50`
  - `scripts/step03_waveforms_from_p_picks.py:138`-`scripts/step03_waveforms_from_p_picks.py:139`
- Materialize tambem usa P*:
  - `scripts/materialize_events_dataset.py:75`-`scripts/materialize_events_dataset.py:76`
  - `scripts/materialize_events_dataset.py:179`-`scripts/materialize_events_dataset.py:180`

### R4 - Janela de 60 s (10 s antes, 50 s depois da P)
Status: OK
- Runner real define defaults 10/50:
  - `scripts/run_real_mg_maglt4_depthlt10.sh:50`-`scripts/run_real_mg_maglt4_depthlt10.sh:51`
  - `scripts/run_real_mg_maglt4_depthlt10.sh:217`-`scripts/run_real_mg_maglt4_depthlt10.sh:218`
- Step03 aplica exatamente no download:
  - `scripts/step03_waveforms_from_p_picks.py:507`-`scripts/step03_waveforms_from_p_picks.py:508` (defaults)
  - `scripts/step03_waveforms_from_p_picks.py:383`-`scripts/step03_waveforms_from_p_picks.py:386` (triplet)
  - `scripts/step03_waveforms_from_p_picks.py:298`-`scripts/step03_waveforms_from_p_picks.py:301` (modo por canal)

### R5 - Triplet 3 canais (HHZ/HHN/HHE)
Status: OK no fluxo real
- Runner real fixa canais HHZ,HHN,HHE:
  - `scripts/run_real_mg_maglt4_depthlt10.sh:52`
  - `scripts/run_real_mg_maglt4_depthlt10.sh:176`-`scripts/run_real_mg_maglt4_depthlt10.sh:177`
  - `scripts/run_real_mg_maglt4_depthlt10.sh:225`
- Step02 grava contrato para Step03:
  - `src/seismic_event_discriminator/step02_fdsn_picks_export.py:235`-`src/seismic_event_discriminator/step02_fdsn_picks_export.py:240`
  - `src/seismic_event_discriminator/step02_fdsn_picks_export.py:446`
- Step03 em modo triplet baixa os 3 canais e falha se faltar algum:
  - `scripts/step03_waveforms_from_p_picks.py:403`-`scripts/step03_waveforms_from_p_picks.py:415`

### R6 - Elegibilidade final e dataset final
Status: OK
- Materialize exige matched, state, mag/depth, P<=400, waveform baixada, arquivo mseed, event.xml:
  - `scripts/materialize_events_dataset.py:202`-`scripts/materialize_events_dataset.py:219`
- Runner real executa materialize como etapa final:
  - `scripts/run_real_mg_maglt4_depthlt10.sh:248`-`scripts/run_real_mg_maglt4_depthlt10.sh:260`

## Evidencias do notebook Step1 (RAW)
Fonte: `notebooks/step1_sisbra_selfcontained.ipynb`.

- `rows_raw_total=5934`
- `rows_keep_in_mg=918`
- `rows_drop_outside_mg=4872`
- `rows_drop_no_valid_coords=144`
- `incons_st_mg_outside=15`
- `incons_st_not_mg_inside=13`
- `incons_st_empty_inside=0`

## Achados (ordenados por severidade)

### S1 - Divergencia entre notebook validado e pipeline operacional no gate MG
- Notebook Step1 valida criterio deterministico por interseccao ponto-poligono.
- Pipeline operacional atual ainda usa `ST` como gate em scripts centrais:
  - `scripts/filter_sisbra_csv.py`
  - `scripts/step03_waveforms_from_p_picks.py`
  - `scripts/materialize_events_dataset.py`
  - `scripts/organize_compatible_events.py`
- Impacto:
  - selecao de eventos pode divergir entre notebook e execucao Python+Bash;
  - inconsistencias de catalogo (`ST` incorreto) podem contaminar o conjunto final.

### S2 - Inconsistencia de origem de datetime entre contrato e implementacao no Step03
- Contrato do Step02 declara `step03_datetime_source = event_origin_utc`:
  - `src/seismic_event_discriminator/step02_fdsn_picks_export.py:238`
- Step03 resolve tag de nome priorizando `sisbra.origin_time` antes de `fdsn.origin_time`:
  - `scripts/step03_waveforms_from_p_picks.py:83`-`scripts/step03_waveforms_from_p_picks.py:89`
- Impacto:
  - nome do arquivo `NET_STA_DATETIME.mseed` pode refletir hora SISBRA e nao hora de origem FDSN, contradizendo o contrato semantico.

### S3 - Defaults de Step03 isolado nao batem com defaults do materialize (fora do runner real)
- Step03 default:
  - `waveforms-subdir=waveforms` em `scripts/step03_waveforms_from_p_picks.py:510`
  - `summary-csv=outputs/waveform_picks_download_summary.csv` em `scripts/step03_waveforms_from_p_picks.py:511`
- Materialize default:
  - `waveforms-subdir=waveform` em `scripts/materialize_events_dataset.py:374`
  - `download-summary-csv=outputs/waveform_triplet_download_summary_events.csv` em `scripts/materialize_events_dataset.py:354`-`scripts/materialize_events_dataset.py:356`
- Impacto:
  - rodar Step03 e materialize manualmente com defaults pode produzir falso negativo de elegibilidade.
- Observacao:
  - no fluxo real (`run_real_mg_maglt4_depthlt10.sh`) isso esta alinhado porque os parametros sao passados explicitamente.

## Pontos importantes do desenho atual
- O filtro de fase P e feito no Step03/materialize, nao no Step02.
- O fluxo atual usa checagem redundante de criterios (filtro inicial + Step03 + materialize), o que aumenta seguranca contra entrada fora da politica.
- Politica de colisao no materialize eh `abort` e evita mistura/sobrescrita silenciosa:
  - `scripts/materialize_events_dataset.py:376`-`scripts/materialize_events_dataset.py:380`
  - `scripts/materialize_events_dataset.py:440`-`scripts/materialize_events_dataset.py:471`

## Recomendacoes objetivas
1. Migrar o gate MG dos scripts para ponto-poligono e manter `ST` apenas como auditoria.
2. Corrigir o Step03 para respeitar o contrato `event_origin_utc` (priorizar `fdsn.origin_time` na tag) ou ajustar explicitamente o contrato para o comportamento atual.
3. Unificar defaults entre Step03 e materialize (`waveform(s)` e nome do summary CSV) para evitar erro em execucao manual fora do runner.
4. Adicionar teste de regressao de contrato para garantir coerencia entre:
   - `waveform_download_contract` do Step02
   - resolucao de `event_datetime_tag` no Step03
   - regras de leitura no materialize.

## Estado geral
- Requisitos funcionais principais (MG por geometria, mag<4, depth<10, P<=400,
  P-10/P+50, triplet HHZ/HHN/HHE) estao implementados e validados em smoke E2E.
- Gaps historicos S1/S2/S3 deste documento foram resolvidos no estado atual da
  codebase; este arquivo permanece como trilha de auditoria da migracao.
