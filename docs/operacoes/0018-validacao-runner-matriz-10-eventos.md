# Operacao 0018 - Validacao do runner de matriz com 10 eventos

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`

## Objetivo

Validar em execucao real o runner da operacao 0017 com `--test-limit 10`,
confirmando:

1. arquivamento correto dos artefatos;
2. ausencia de contaminacao por logs antigos;
3. comportamento atual das etapas do fluxo legado.

## Comando executado

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh --test-limit 10
```

## Evidencias geradas

1. Sumario da matriz:
   - `docs/operacoes/anexos/0018-matriz-testes-fluxo-sismo-10.tsv`
2. Log da falha de pos-processamento:
   - `docs/operacoes/anexos/0018-falha-pos-pick-prob-nat.log`
3. Diretorio de arquivamento bruto:
   - `.specs/codebase/arquivos/registros/test_matrix/20260210_170316/`

## Resultado da matriz

1. `pre` -> `rc=0`
2. `eventos` -> `rc=1`
3. `predict` -> `rc=0`
4. `pos` -> `rc=1`
5. `maps` -> `rc=0`
6. `report` -> `rc=0`
7. `todos` -> `rc=1`

## Diagnostico

1. Correcao da operacao 0017 validada:
   - o arquivo de arquivamento `20260210_170316` nao trouxe subpastas antigas
     de execucoes anteriores.
2. `eventos`/`todos` continuam falhando fora do contexto de rede IAG,
   comportamento esperado para dependencia de FDSN/event.
3. `pos` falhou com `KeyError: ['Pick Prob_Nat']`, indicando dependencia de
   formato/colunas de entrada que nao foi satisfeita no estado gerado por
   `predict` nesta execucao.

## Decisao

Nao corrigir o comportamento de `pos` nesta operacao. O objetivo aqui foi
validar o runner e registrar o estado real do legado. A correcao funcional de
contratos entre `-pr` e `-po` fica para operacao dedicada.

## Proximo passo

Abrir operacao especifica para contrato de dados entre predicao e
pos-processamento (colunas minimas esperadas por `pos_processa.py`).
