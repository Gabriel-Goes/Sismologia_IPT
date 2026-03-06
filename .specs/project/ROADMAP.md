# ROADMAP

## Decisao transversal (2026-03-02)
- Filtro geografico de MG passa a ser deterministico por coordenadas (ponto-poligono).
- Campos `ST`, toponimias e localidades ficam apenas como auditoria de consistencia.
- Fonte primaria do poligono de MG: GeoPackage local sincronizado via `rsync` do GeoServer
  (fallback para `geobr` somente quando necessario).
- Fonte canonica do SISBRA passa a ser o `RAW`; o projeto materializa seus
  proprios CSVs derivados e nao assume `CLEAN` como entrada confiavel.

## M0 - Bootstrap cleanroom (done)
- Branch cleanroom criada.
- Snapshot do legado arquivado.
- Estrutura inicial de notebooks e script linear criada.

## M1 - Etapas 1+2: Catalogo e selecao (done)
### Goal
Ler catalogo (`QuakeML` ou texto de builder), selecionar eventos alvo e quebrar
em arquivos por evento (`xml|json`) para alimentar a etapa 3.

### Deliverables
- Notebook de selecao (etapas 1+2).
- Export por evento de metadados iniciais.
- Lista de eventos selecionados para aquisicao.

### Verification
- Regras de filtro reproduziveis (regiao, magnitude, profundidade).
- Contagem de eventos antes/depois registrada.

## M1.1 - Alinhamento notebook -> pipeline Python+Bash (done, smoke validado em 2026-03-04)
### Goal
Levar para os scripts operacionais a mesma regra validada no notebook Step1:
inclusao de evento em MG por interseccao ponto-poligono, com `ST` apenas para
auditoria.

### Discovery baseline (Step1 RAW)
- `rows_raw_total=5934`
- `rows_keep_in_mg=918`
- `rows_drop_outside_mg=4872`
- `rows_drop_no_valid_coords=144`
- `incons_st_mg_outside=15`
- `incons_st_not_mg_inside=13`
- `incons_st_empty_inside=0`

### Deliverables
- Documentacao de estado atual vs estado alvo em `.specs` e `docs/`.
- Etapa explicita `RAW -> normalized -> filtered` no pipeline oficial.
- Checklist tecnico fechado de migracao para:
  - `scripts/normalize_sisbra_raw.py`
  - `scripts/filter_sisbra_csv.py`
  - `scripts/step03_waveforms_from_p_picks.py`
  - `scripts/materialize_events_dataset.py`
  - `scripts/organize_compatible_events.py`
  - `scripts/run_real_mg_maglt4_depthlt10.sh`
- Politica de compatibilidade temporaria:
  - manter `--state`/`--state-filter` na CLI;
  - marcar como parametro de auditoria/deprecacao para gate geografico.

### Verification
- Mesma entrada de catalogo gera contagens iguais entre notebook Step1 e
  pipeline migrado para o gate geografico.
- CSV normalizado derivado do `RAW` e CSV de rejeitados sem coordenadas validas
  ficam auditaveis e reproduziveis.
- Tabelas de inconsistencias `ST x geometria` disponiveis para auditoria.
- Sem fallback silencioso para `ST` no criterio de inclusao em MG.

### Validation update (2026-03-04, smoke controlado)
- Execucao E2E com `seed=42`, amostra `n=300`:
  - input smoke: `outputs/smoke/sisbra_clean_smoke_seed42_n300.csv`
  - filtro: `rows_in=300`, `passed_geo_inside_mg=51`, `rows_out=14`
  - Step02: `matched=14`, `no_match=0`, `ambiguous=0`, `error=0`
  - Step03: `triplet_tasks=75`, `downloaded=58`, `error=17` (HTTP 204 no data)
  - materialize: `eligible=14`, `moved=14`, sem colisao
- Artefatos:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260304T121721Z.md`
  - `outputs/smoke/waveform_triplet_download_summary_smoke.csv`
  - `outputs/smoke/events_materialize_report_smoke.csv`

### Validation update (2026-03-06, trilha RAW derivada)
- Normalizacao do `RAW`:
  - `rows_raw_total=5934`
  - `rows_valid_coords=5790`
  - `rows_invalid_coords=144`
- Filtro operacional no derivado normalizado:
  - `passed_geo_inside_mg=918`
  - `rows_out=210`
  - `dropped_geo_outside_mg=4872`
  - `dropped_geo_no_valid_coords=144`
- Conclusao:
  - notebook Step1 e filtro oficial passam a convergir sobre a mesma fonte
    canonica (`RAW`), eliminando a dependencia operacional do `CLEAN`.

## M1.2 - Validacao E2E em lote completo (done, rerun validado em 2026-03-06)
### Goal
Repetir o fluxo E2E no catalogo `RAW` completo, passando pela etapa de
normalizacao propria, para fechar a validacao operacional antes de avancar
para M2.

### Verification
- Runner `run_real_mg_maglt4_depthlt10.sh` finaliza com `rc=0`.
- Runner gera e registra:
  - CSV normalizado derivado do `RAW`;
  - CSV de rejeitados sem coordenadas validas;
  - CSV filtrado operacional para Step02.
- Relatorios de smoke e lote completo permanecem coerentes no criterio de gate.
- Taxa de `error` no Step03 fica auditada por estacao/canal para triagem.

### Validation update (2026-03-06, primeira execucao em lote completo)
- Filtro operacional:
  - `rows_in=5934`
  - `passed_geo_inside_mg=918`
  - `rows_out=210`
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
  - `eligible=188`
  - `collision_count=2`
  - `moved=0` porque `collision_policy=abort`
- Bloqueio encontrado:
  - duas linhas do SISBRA (`rownum_source=4875` e `4878`) colapsam no mesmo
    `fdsn.origin_time`, gerando o alvo `2021078T053957` e abortando a
    materializacao final.
- Conclusao:
  - a trilha `RAW -> normalized -> filtered -> Step02 -> Step03` esta validada
    em lote completo;
  - falta definir e implementar a politica de deduplicacao/colisao para fechar
    M1.2 com `rc=0`.

### Validation update (2026-03-06, rerun com `merge_by_fdsn`)
- Politica adotada:
  - um unico evento final por `fdsn.resource_id`
  - linhas SISBRA duplicadas ficam auditadas em `event.json` e em relatorio CSV/MD
- Step02:
  - `matched=190`
  - `no_match=19`
  - `ambiguous=1`
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
  - `smi:org.gfz-potsdam.de/geofon/usp2021flcy`
  - canonico: `20210319T053957_usp2021flcy_row44`
  - duplicado absorvido: `20210319T053957_usp2021flcy_row45`
- Artefatos:
  - `outputs/logs_real_events/run_real_mg_maglt4_depthlt10_20260306T005607Z.md`
  - `outputs/events_materialize_report_m12_merge_v2.csv`
  - `outputs/events_duplicate_merge_report_m12_merge_v2.csv`
- Conclusao:
  - M1.2 fica fechado com `rc=0`;
  - o pipeline passa a tratar explicitamente o caso “duas linhas SISBRA -> um evento FDSN”.

## M2 - Etapa 3: Base local incremental de analise
### Goal
Criar base local por evento com metadados + waveform.

### Deliverables
 **ALGORITMOS DE CELINE HOURCAD SOLICITA ESTRUTURA FIXA. VIDE EXEMPLO ABAIXO:**
#### EXEMPLO DO REPOSITÓRIO DE CELINE HOURCAD
   Dataset
To apply the algorithm, we need a folder architecture:
    - mseed_demo/
        - 2022004T134407/
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed

#### PROPOSTA DE NOVA ESTRUTURA DE DADOS
**PODEMOS PROPOR ALGO ENTRE O QUE BIANCHI SUGERE E O QUE HOURCAD DEFINE**
    - NDS/
        - YYYYMMDDTHHMMSS/
            - NET_STA_YYYYMMDDTHHMMSS.json **UM PARA CADA EVENTO**
            - NET_STA_YYYYMMDDTHHMMSS.mseed **UM PARA CADA PICK**
        - 2022004T134407/
            - 2022004T134407.json
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed
**JSON DEVE SER EXPANDÍVEL PARA MAIS INFO COMO RESULTADO DA CNN, SNR, ETC**

### Verification
- Reexecucao nao perde nem duplica eventos ja persistidos.
- Adicao de novos eventos sem reprocessar base completa.

## M3 - Etapa 4: Inferencia CNN paralelizavel
### Goal
Executar inferencia por evento com suporte a paralelismo simples.

### Deliverables
- Script de inferencia por evento.
- Runner de lote paralelo (shell ou python).
- Saida por evento em `prediction.json` ou embutida em `event.json`.  **EMBUTIR EM JSON É ELEGANTE**

### Verification
- Lote de teste executa com resultados consistentes. **LOTE DE TESTES DEVE USAR EVENTOS ALEATÓRIOS DO CATÁLOGO SEMPRE COM 42 COMO SED**
- Escala linear basica ao aumentar workers.

## M4 - Etapa 5: Analise e comunicacao de resultados
### Goal
Consolidar resultados em notebooks para avaliacao cientifica.

### Deliverables
- Notebooks de graficos e mapas.
- Export de tabelas e figuras principais.
- Material pronto para discussao com orientadores.

### Verification
- Pipeline completo reproduzivel em ambiente SEISAPP.
- Resultados

## M5 - Contexto minerario ANM para priorizacao (future)
### Goal
Incorporar vetores oficiais da Agencia Nacional de Mineracao (ANM) para
priorizar eventos em regioes de maior atividade mineraria e apoiar a validacao
dos resultados da rede neural.

### Deliverables
- Ingestao vetorial ANM com versionamento de fonte e data de referencia.
- Camada espacial derivada com atributos relevantes (substancia, estagio da
  atividade, status operacional).
- Regra de priorizacao por proximidade de origem sismica a minas ativas.
- Indicadores de consistencia para classificacao antropogenica:
  - maior confianca quando proximo de atividade mineraria ativa;
  - alerta de possivel falso positivo quando distante de atividade mineraria.

### Verification
- Pipeline espacial reprodutivel e auditavel (mesma entrada -> mesmo resultado).
- Relatorio comparando evento classificado vs contexto minerario de entorno.
- Lista de casos inconsistentes para revisao com professores e responsaveis
  pelo catalogo.
