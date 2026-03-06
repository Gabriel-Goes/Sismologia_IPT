# STATE

## Last Update
2026-03-04

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
4. Ausencia de testes unitarios formais para schema/naming (dependencia de smoke operacional).

## Next Action
Executar validacao da nova trilha `RAW -> normalized -> filtered` e consolidar:
1. paridade notebook Step1 vs `filter_sisbra_csv.py` usando o mesmo `RAW`;
2. smoke E2E consumindo o CSV filtrado derivado do `RAW`;
3. taxa de `HTTP 204` por rede/estacao/canal no Step03 para triagem;
4. criterio de passagem para iniciar M2 no fluxo operacional.
