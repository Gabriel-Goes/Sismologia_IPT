# STATE

## Last Update
2026-03-18

## Current Branch
`main`

## Confirmed Decisions
1. Etapas 1 e 2 permanecem em um unico processo operacional (Step02 atual).
2. Step03 deve suportar dois formatos durante transicao:
   - legado split por canal: `NET.STA.LOC.CHA_PICKTIME.mseed`
   - alvo consolidado: `NET_STA_DATETIME.mseed`
3. Estrutura final de eventos compativeis permanece:
   - `data/eventos_compativeis/YYYYMMDDTHHMMSS/waveforms/*.mseed`
4. Inferencia RNC deve escrever resultado no `event.json` (`rnc_prediction`) e
   manter CSVs de auditoria.
5. Amostragem de teste aleatorio deve usar `seed=42`.
6. Criterio alvo pre-RNC em `data/events` (aprovado em 2026-03-02):
   - filtro geografico de MG por coordenadas (interseccao ponto-poligono),
     sem depender de `state`/toponimia/localidade como criterio de inclusao
   - `magnitude < 4`, `depth_km < 10`
   - pick `P* <= 400 km`, janela `P-10s/P+50s`, canais `HHZ,HHN,HHE`
7. Regra de seguranca para output final:
   - `data/events` deve estar vazio; o wrapper aborta se encontrar conteudo
     (sem limpeza automatica/destrutiva).
8. Scripts de diagnostico historico ficam em `scripts/legacy/`.
9. Fonte canonica de arquitetura e planejamento:
   - `.specs/project/`, `.specs/codebase/`, `.specs/features/`.
10. Compatibilidade de CLI durante migracao:
   - manter `--state`/`--state-filter` por compatibilidade;
   - tratar esses campos como auditoria/deprecacao no criterio geografico alvo.
11. Baselines externos para implementacao futura confirmados:
   - `~/projetos/ipt/SISMO/catalogo` como referencia para camada de adapters de catalogo;
   - `~/projetos/ipt/SISMO/QA_SISMO/vetor_minerario` como referencia para enriquecimento ANM e QA STAC;
   - integracao no Classificador deve usar schema canonico e modulos opcionais
     desacoplados do caminho critico Step02->Step03->RNC.
12. Fonte primaria do poligono de MG (2026-03-03):
   - usar GeoPackage local sincronizado via `rsync` do GeoServer
     (`/home/gabrielgoes/geodatabase.gpkg`, camada `ibge_mg_uf_2024`);
   - manter `geobr` apenas como fallback quando o arquivo local nao estiver disponivel.
13. Endpoint operacional em SEISAPP:
   - usar `CLIENT_URL=http://10.110.0.134` para FDSN interno;
   - `127.0.0.1:28080` permanece apenas para cenarios com tunel local valido.
14. Fonte canonica SISBRA (2026-03-06):
   - usar `catalogo_RAW_v2024May09.csv` como entrada de referencia;
   - gerar CSV normalizado e CSV de rejeitados sem coordenadas validas dentro do
     proprio pipeline;
   - `catalogo_CLEAN_v2024May09.csv` deixa de ser default operacional.
15. Politica oficial de duplicacao SISBRA->FDSN (2026-03-06):
   - quando multiplas linhas SISBRA casam com o mesmo `fdsn.resource_id`,
     materializar um unico evento final;
   - manter a linha canonica em `sisbra` e registrar as demais em
     `sisbra_duplicates` + `dedup`;
   - continuar abortando colisoes que nao possam ser explicadas pelo mesmo
     `fdsn.resource_id`.

## Notebook Evidence (Step1 RAW, 2026-03-02)
- Fonte: `notebooks/step1_sisbra_selfcontained.ipynb` (execucao registrada no proprio notebook).
- Totais:
  - `rows_raw_total=5934`
  - `rows_keep_in_mg=918`
  - `rows_drop_outside_mg=4872`
  - `rows_drop_no_valid_coords=144`
- Inconsistencias ST x geometria:
  - `incons_st_mg_outside=15`
  - `incons_st_not_mg_inside=13`
  - `incons_st_empty_inside=0`
- Conclusao confirmada:
  - `ST`/toponimia/localidade nao sao confiaveis como gate principal para MG;
    devem permanecer como auditoria de consistencia.

## Implementation Status (2026-03-02)
- Notebook Step1 ja usa regra deterministica por ponto-poligono.
- Pipeline Python+Bash foi migrado para gate geografico deterministico em:
  - `scripts/filter_sisbra_csv.py`
  - `scripts/step03_waveforms_from_p_picks.py`
  - `scripts/materialize_events_dataset.py`
  - `scripts/organize_compatible_events.py`
  - `scripts/run_real_mg_maglt4_depthlt10.sh`
- `--state`/`--state-filter` foram mantidos por compatibilidade como auditoria.
- Filtro de ano (`min-year`) foi movido para o ultimo gate nos scripts migrados.
- Gate de MG agora suporta fonte local offline por GeoPackage (`--mg-polygon-gpkg`/`--mg-polygon-layer`).

## RAW Normalization Migration (2026-03-06)
- Nova etapa explicita adicionada:
  - `scripts/normalize_sisbra_raw.py`
- Artefatos derivados padrao:
  - `outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalized_v2024May09.csv`
  - `outputs/catalogs/sisbra_v2024May09/sisbra_raw_rejected_no_valid_coords_v2024May09.csv`
  - `outputs/catalogs/sisbra_v2024May09/sisbra_raw_mg_maglt4_depthlt10_yearge2020_v2024May09.csv`
- Leitores SISBRA do Step01/Step02 passam a aceitar preferencialmente:
  - `latit_num`, `longit_num`, `ST_norm`
- Wrapper principal `run_real_mg_maglt4_depthlt10.sh` agora orquestra:
  - normalize RAW -> filter -> Step02 -> Step03 -> materialize

## RAW Validation Check (2026-03-06)
- Normalizacao do `RAW`:
  - `rows_raw_total=5934`
  - `rows_valid_coords=5790`
  - `rows_invalid_coords=144`
- Filtro operacional sobre o derivado normalizado:
  - `rows_in=5934`
  - `passed_geo_inside_mg=918`
  - `rows_out=210`
  - `dropped_geo_outside_mg=4872`
  - `dropped_geo_no_valid_coords=144`
  - `st_geo_inconsistent_rows=28`
  - `st_geo_unknown_rows=6`
- Interpretacao:
  - a paridade com o notebook fica confirmada no gate geografico central
    (`918` dentro de MG, `4872` fora, `144` sem coordenadas validas);
  - os `28` casos inconsistentes correspondem aos 15 casos `ST=MG` fora de MG
    e 13 casos `ST!=MG` dentro de MG;
  - `rows_out=210` e o total operacional apos aplicar
    `mag<4`, `depth<10`, `year>=2020` sobre o `RAW`.

## RAW E2E Smoke (2026-03-06)
- Wrapper:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T002314Z.md`
- Amostra:
  - `rows_raw_total=300`
  - `rows_valid_coords=292`
  - `rows_invalid_coords=8`
- Filtro:
  - `passed_geo_inside_mg=43`
  - `rows_out=8`
- Step02:
  - `matched=7`
  - `ambiguous=1`
  - `no_match=0`
- Step03:
  - `triplet_tasks=34`
  - `downloaded=26`
  - `error=8`
- Materialize:
  - `event_json_found=7`
  - `eligible=7`
  - `moved=7`
- Conclusao:
  - a nova orquestracao `RAW -> normalized -> filtered -> Step02 -> Step03 -> materialize`
    executa com sucesso.

## RAW E2E Full Run (M1.2, 2026-03-06)
- Wrapper:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T002948Z.md`
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T002948Z.log`
- Filtro operacional:
  - `rows_in=5934`
  - `passed_geo_inside_mg=918`
  - `rows_out=210`
- Step02:
  - `matched=190`
  - `no_match=19`
  - `ambiguous=1`
  - `error=0`
- Auditoria no-match/ambiguous:
  - `events=20`
  - `severity_counts={'critical': 4, 'high': 1, 'medium': 15}`
- Step03:
  - `events_selected=190`
  - `triplet_tasks=996`
  - `downloaded=823`
  - `error=173`
- Materialize:
  - `event_json_found=190`
  - `eligible=188`
  - `collision_count=2`
  - `moved=0`
  - `aborted_collision=2`
- Bloqueio identificado:
  - duas linhas SISBRA (`rownum_source=4875` e `4878`) casam com o mesmo
    `fdsn.origin_time=2021078T053957`, produzindo o mesmo `target_folder`
    `2021078T053957`;
  - com `collision_policy=abort`, o wrapper interrompe no passo de
    materializacao e M1.2 ainda nao fecha com `rc=0`.
- Interpretacao:
  - a parte de aquisicao (`normalize -> filter -> Step02 -> Step03`) ficou
    operacional em lote completo;
  - o proximo gargalo real esta na politica de deduplicacao/colisao do dataset
    final.

## RAW E2E Full Run (M1.2 resolved, 2026-03-06)
- Wrapper:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T005607Z.md`
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T005607Z.log`
- Reexecucao:
  - roots novos (`data/events_stage_m12_merge_v2`, `data/events_stage_non_matched_m12_merge_v2`, `data/events_m12_merge_v2`)
  - politica `collision_policy=merge_by_fdsn`
- Step02:
  - `matched=190`
  - `no_match=19`
  - `ambiguous=1`
  - `error=0`
- Step03:
  - `triplet_tasks=996`
  - `downloaded=823`
  - `error=173`
- Materialize:
  - `event_json_found=190`
  - `eligible=189`
  - `moved=189`
  - `merged_duplicate=1`
  - `collision_count=0`
- Caso consolidado:
  - `fdsn.resource_id=smi:org.gfz-potsdam.de/geofon/usp2021flcy`
  - canonico: `20210319T053957_usp2021flcy_row44` (`rownum_source=4875`)
  - absorvido: `20210319T053957_usp2021flcy_row45` (`rownum_source=4878`)
- Novos artefatos de auditoria:
  - `outputs/events_materialize_report_m12_merge_v2.csv`
  - `outputs/events_materialize_report_m12_merge_v2.md`
  - `outputs/events_duplicate_merge_report_m12_merge_v2.csv`
  - `outputs/events_duplicate_merge_report_m12_merge_v2.md`
- Estrutura do `event.json` final:
  - `sisbra` continua sendo a linha canonica;
  - `dedup` descreve a chave de merge e o grupo consolidado;
  - `sisbra_duplicates` preserva as linhas SISBRA absorvidas para auditoria.
- Conclusao:
  - M1.2 fica fechado com `rc=0`;
  - a descoberta cientifica “duas linhas SISBRA para um evento FDSN” passa a ser
    tratada explicitamente no pipeline final.

## Filter Check (full CLEAN, 2026-03-04)
- Comando:
  - `python3 scripts/filter_sisbra_csv.py --input-csv catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv --output-csv outputs/smoke/sisbra_mg_maglt4_depthlt10_fullcheck.csv --mg-polygon-gpkg ~/geodatabase.gpkg --mg-polygon-layer ibge_mg_uf_2024`
- Resultado:
  - `rows_in=5571`
  - `passed_geo_inside_mg=889`
  - `rows_out=207`
  - `dropped_geo_outside_mg=4681`
  - `dropped_geo_no_valid_coords=1`
  - `st_geo_inconsistent_rows=26`

## E2E Smoke Evidence (2026-03-04)
- Run:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260304T121721Z.md`
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260304T121721Z.log`
- Input smoke:
  - `outputs/smoke/sisbra_clean_smoke_seed42_n300.csv` (seed=42, n=300)
- Resultado por etapa:
  - filtro: `rows_in=300`, `passed_geo_inside_mg=51`, `rows_out=14`
  - Step02: `matched=14`, `no_match=0`, `ambiguous=0`, `error=0`
  - Step03: `events_selected=14`, `triplet_tasks=75`, `downloaded=58`, `error=17`
  - materialize: `event_json_found=14`, `eligible=14`, `moved=14`
- Auditoria `ST x geometria` no smoke:
  - `events_state_inconsistent_audit=0`
  - `events_state_unknown_audit=0`
- Observacao:
  - erros de Step03 sao `HTTP 204 No data available for request` em parte dos
    canais/estacoes, sem impedir elegibilidade dos 14 eventos.

## Active Feature Set
- `01-catalogo-selecao`
- `03-base-local-eventos`
- `04-inferencia-cnn-paralela`
- `05-analise-resultados`

## Codebase Baseline (2026-02-28)

Criada a base de mapeamento em `.specs/codebase/`:

- `STACK.md`
- `ARCHITECTURE.md`
- `CONVENTIONS.md`
- `STRUCTURE.md`
- `TESTING.md`
- `INTEGRATIONS.md`

Escopo do baseline:
- pipeline ativo que gera os `.mseed` atuais
- prioridade P0 em arquivos realmente executados nas ultimas iteracoes
- evidencias por arquivo:linha para reduzir custo de contexto

## Maintenance Policy For `.specs/codebase`

Regra geral:
- atualizar P0 em toda iteracao que altere fluxo ou output.
- atualizar P1 quando houver mudanca em gate triplet, merge ou inferencia.
- atualizar P2 somente quando runbook/ambiente mudar.

P0:
1. `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
2. `scripts/step03_waveforms_from_p_picks.py`
3. `scripts/organize_compatible_events.py`
4. `outputs/waveform_triplet_download_summary_mg.csv` (ou ultimo summary equivalente)
5. `outputs/logs_*/run_all_sisbra_<UTC>.md` (ultimo run de referencia)

## Current Risks
1. Dependencia de rede e de execucao fora do sandbox para validacao FDSN fim-a-fim.
2. Drift entre versao de script e artefatos de `outputs/` (timestamp/header).
3. Retornos `HTTP 204` no Step03 podem reduzir cobertura de canais em parte dos eventos.
4. Ausencia de testes unitarios formais para schema/naming/deduplicacao (dependencia de smoke operacional).

## Notebook Audit Layer (2026-03-06)
- Criados notebooks didaticos self-contained:
  - `notebooks/step2_sisbra_fdsn_duplicate_audit_selfcontained.ipynb`
  - `notebooks/step3_m12_audit_selfcontained.ipynb`
- Ambos seguem `docs/tlc_diretrizes_jupyter_notebooks.md`:
  - sem `class`
  - sem `def`
  - leitura linear por celulas
  - sem importar scripts Python do repositorio
- Validacao:
  - executados com `jupyter nbconvert --execute`
  - `step2` audita o caso `usp2021flcy` e mostra `dedup + sisbra_duplicates`
  - `step3` resume o rerun `m12_merge_v2` e ja gera triagens iniciais de `HTTP 204`
- Artefatos auxiliares produzidos em runtime ficam sob `outputs/tables/` e `outputs/figures/` (ignorados pelo git).

## M3 RNC Inference (2026-03-18)
- Ambiente:
  - `pyenv 2.6.26` instalado em seisapp
  - virtualenv `geo-seis-rnc` (Python 3.11.9, TensorFlow 2.21.0, ObsPy 1.5.0)
  - `pyenv local geo-seis-rnc` configurado no repositorio (`.python-version`)
  - Script de setup: `scripts/dev/setup_pyenv_project.sh --env geo-seis-rnc --python 3.11.9 --with-rnc --set-local`
- Decisao: pyenv-virtualenv em seisapp como ambiente padrao para RNC inference
- Smoke test:
  - `--limit-events=5`, `--workers=1`
  - `status_counts={'ok': 5}`
  - 4 Natural, 1 Anthropogenic
- Full run:
  - `--compatible-root=data/events_m12_merge_v2`
  - `--waveforms-subdir=waveform`
  - `--workers=4`, `--no-skip-existing`
  - `model_sha256=574b7084f06a6e8b890a1f479cab39725cf9889ecd5b25057bd86073796a9881`
  - `total_events=189`
  - `status_counts={'ok': 183, 'partial': 6}`
  - `label_counts={'Natural': 175, 'Anthropogenic': 14}`
  - `total_picks=821`, `picks_ok=814`, `picks_error=7`
- Erros de preprocessamento (7 picks em 6 eventos):
  - Causa unica: `invalid spectrogram shape` — waveforms com duracao
    insuficiente para gerar os 237 frames esperados (60s janela)
  - Estacoes afetadas: BB19B, CANS, PMNB, DIAM, JANB
- Artefatos:
  - `outputs/rnc_prediction_events_m12v2.csv`
  - `outputs/rnc_prediction_picks_m12v2.csv`
  - `outputs/rnc_prediction_errors_m12v2.csv`
  - Cada `event.json` atualizado com bloco `rnc_prediction`
- Verificacao:
  - `event.json` de evento arbitrario (`2022326T163421`) contem `rnc_prediction.summary`
  - CSV de eventos tem 189 linhas com classificacao consistente

## M4 Notebooks de Auditoria RNC (2026-03-18)
- Criados notebooks self-contained:
  - `notebooks/step4_rnc_inference_selfcontained.ipynb`
    - Demonstra preprocessamento e inferencia CNN em 3 eventos exemplo
    - Funcoes auxiliares replicam `rnc_infer.py` com justificativa em Markdown
    - Visualiza waveforms brutos e espectrogramas 3C
  - `notebooks/step5_results_analysis_selfcontained.ipynb`
    - Distribuicao de classe (Natural vs Antropogenico)
    - Mapa espacial de MG com poligono do GeoPackage
    - Analise de confianca e eventos de baixa confianca
    - Analise por estacao (frequencia e taxa de erro)
    - Analise temporal (ano e mes)
    - Tabela consolidada exportada como CSV
- Ambos seguem `docs/tlc_diretrizes_jupyter_notebooks.md`
- Step4 usa funcoes auxiliares com justificativa (excecao prevista nas diretrizes)

## Next Action
Proxima triagem operacional:
1. executar notebooks step4 e step5 com `jupyter nbconvert --execute` para validacao;
2. revisar com os professores os 14 eventos classificados como Antropogenico;
3. analisar eventos de baixa confianca para possivel revisao manual;
4. decidir quando fazer push remoto.
