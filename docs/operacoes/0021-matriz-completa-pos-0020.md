# Operacao 0021 - Matriz completa (10 eventos) apos correcao 0020

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `legado`  
**Status:** `concluida`

## Objetivo

Validar a bateria completa de flags do `fluxo_sismo.sh` com `--test-limit 10`
apos a estabilizacao do contrato entre predicao e pos-processamento
(operacao 0020).

## Comando executado

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh --test-limit 10
```

## Evidencias

1. Matriz completa consolidada:
   - [0021-matriz-completa-10.tsv](/anexos/anexo-0021-matriz-completa-10-tsv)
2. Falha da etapa `-e` por indisponibilidade FDSN no host atual:
   - [0021-falha-eventos-fdsn.log](/anexos/anexo-0021-falha-eventos-fdsn-log)
3. Falha de `todos` herdada da etapa `-e`:
   - [0021-falha-todos-fdsn.log](/anexos/anexo-0021-falha-todos-fdsn-log)

## Resultado

1. `pre` -> `rc=0`
2. `eventos` -> `rc=1`
3. `predict` -> `rc=0`
4. `pos` -> `rc=0`
5. `maps` -> `rc=0`
6. `report` -> `rc=0`
7. `todos` -> `rc=1`

## Interpretacao

1. A regressao introduzida entre `-pr` e `-po` foi eliminada:
   - `pos` manteve `rc=0` na matriz completa.
2. O bloqueio restante continua externo ao codigo desta branch:
   - conectividade/servico `event` dos endpoints FDSN fora do ambiente IAG.
3. O estado atual do legado em ambiente local fica consolidado como:
   - etapa de aquisicao dependente de rede IAG;
   - demais etapas estaveis no modo de teste com artefatos locais.

## Proximo passo

Executar a mesma matriz (`--test-limit 10`) no ambiente IAG/SEISAPP para validar
`eventos` e `todos` com acesso ao servico `event` do SeisComP/USP.
