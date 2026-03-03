# STATE

## Last Update
2026-03-03

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
- Pipeline Python+Bash de producao ainda contem gates por `ST` em scripts-chave.
- Migracao de scripts fica registrada no roadmap e ainda nao foi implementada neste ciclo.

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
1. Instabilidade de conectividade FDSN/tuneis (seisArc/UnB).
2. Drift entre versao de script e artefatos de `outputs/` (timestamp/header).
3. Coexistencia de naming legado e novo para `.mseed` pode gerar confusao de diagnostico.
4. Ausencia de testes unitarios formais para schema/naming (dependencia de smoke operacional).

## Next Action
Executar a migracao controlada dos gates de `ST` para ponto-poligono nos
scripts do pipeline, mantendo compatibilidade de CLI e validando paridade
com o notebook Step1.
