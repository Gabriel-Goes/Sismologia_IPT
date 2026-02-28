# STATE

## Last Update
2026-02-28

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
6. Fluxo operacional pre-RNC em `data/events` usa criterios estritos:
   - `state == MG`, `magnitude < 4`, `depth_km < 10`
   - pick `P* <= 400 km`, janela `P-10s/P+50s`, canais `HHZ,HHN,HHE`
7. Regra de seguranca para output final:
   - `data/events` deve estar vazio; o wrapper aborta se encontrar conteudo
     (sem limpeza automatica/destrutiva).
8. Scripts de diagnostico historico ficam em `scripts/legacy/`.
9. Fonte canonica de arquitetura e planejamento:
   - `.specs/project/`, `.specs/codebase/`, `.specs/features/`.

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
Executar `scripts/run_real_mg_maglt4_depthlt10.sh` e validar o dataset final
em `data/events/YYYYJJJTHHMMSS` antes de iniciar a etapa RNC.
