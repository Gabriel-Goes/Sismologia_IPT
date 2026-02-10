# Operacao 0020 - Contrato `-pr` -> `-po` para cenarios sem dados

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `legado`  
**Status:** `concluida`

## Objetivo

Eliminar a quebra do `-po` quando `predito.csv` chega vazio ou com schema
parcial apos `-pr` em modo de teste.

## Problema observado

Na operacao 0018, o pos-processamento falhou com `KeyError` por ausencia de
colunas esperadas em `predito.csv` (ex.: `Pick Prob_Nat`).

Em reteste tecnico, o erro evoluiu para `KeyError: 'SNR_P'` quando nao havia
picks validos para calculo de SNR.

## Escopo executado

1. Estabilizacao de schema no output de predicao:
   - arquivo: `.specs/codebase/fonte/rnc/prediction.py`
   - acao: inicializacao defensiva das colunas de predicao/evento mesmo com
     DataFrame vazio.
2. Fortalecimento da leitura no pos-processamento:
   - arquivo: `.specs/codebase/fonte/analise_dados/pos_processa.py`
   - acao: garantir colunas minimas (`MLv`, `Distance`, `Cat`, `Event Pred`,
     `Pick Prob_Nat`, `SNR_P`, `SNR_S`, `Noise`, `p`) com fallback para `NaN`.
3. Encerramento limpo de `-po` sem dados:
   - `main()` passa a salvar saidas vazias e retornar sem excecao quando
     nao houver picks validos apos filtros.

## Validacao

Teste executado:

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh --cases predict,pos --test-limit 10
```

Evidencias:

1. Matriz curta (`predict,pos`):
   - [0020-matriz-predict-pos-10.tsv](/anexos/anexo-0020-matriz-predict-pos-10-tsv)
2. Log de `-po` sem quebra:
   - [0020-pos-sem-dados.log](/anexos/anexo-0020-pos-sem-dados-log)

Resultado:

1. `predict` -> `rc=0`
2. `pos` -> `rc=0`

## Conclusao

O contrato entre `-pr` e `-po` ficou robusto para o caso "sem dados",
evita falha por `KeyError` e preserva o comportamento rastreavel do legado em
modo teste.

## Proximo passo

Executar matriz completa (`pre,eventos,predict,pos,maps,report,todos`) com
`--test-limit 10` para confirmar regressao zero apos esta correcao.
