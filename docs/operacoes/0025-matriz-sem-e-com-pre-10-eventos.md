# Operacao 0025 - Matriz sem -e com pre (10 eventos)

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `legado`  
**Status:** `concluida`  
**Fase:** `execucao-legado`  
**Tag:** `teste-execucao`

## Objetivo

Executar uma matriz local sem aquisicao (`-e`) incluindo pre-processamento,
para validar o comportamento integrado de:

1. `-pe` (pre-processamento)
2. `-pr` (predicao)
3. `-po` (pos-processamento)
4. `-m` (mapas)
5. `-r` (relatorio)

com `--test-limit 10`.

## Comando executado

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh \
  --cases pre,predict,pos,maps,report \
  --test-limit 10
```

**Archive ID:** `20260211_084132`

## Evidencias

1. Matriz consolidada:
   - [0025-matriz-sem-e-com-pre-10.tsv](/anexos/anexo-0025-matriz-sem-e-com-pre-10-tsv)
2. Contexto de execucao (ambientes/casos):
   - [0025-manifest.env](/anexos/anexo-0025-manifest-env)
3. Log da etapa `pre`:
   - [0025-pre-10.log](/anexos/anexo-0025-pre-10-log)
4. Log da etapa `predict` (0 eventos):
   - [0025-predict-0-eventos.log](/anexos/anexo-0025-predict-0-eventos-log)
5. Log da etapa `pos` (sem picks validos):
   - [0025-pos-sem-picks.log](/anexos/anexo-0025-pos-sem-picks-log)

## Resultado

1. `pre` -> `rc=0`
2. `predict` -> `rc=0`
3. `pos` -> `rc=0`
4. `maps` -> `rc=0`
5. `report` -> `rc=0`

## Interpretacao

1. A trilha sem `-e` permanece executavel ponta a ponta para as etapas
   posteriores, com retorno de sucesso em todos os casos desta matriz.
2. Mesmo com `pre` executado, `predict` seguiu com:
   - `Modo de teste RNC: 0 eventos unicos selecionados (0 picks)`.
3. `pos` respondeu de forma consistente ao estado de entrada:
   - `Sem picks validos para pos-processamento; gerando saida vazia.`
4. A diferenca entre "pipeline executa" e "pipeline produz classificacao"
   ficou explicita nesta iteracao:
   - execucao tecnica: valida;
   - volume util para classificacao: nulo no recorte atual (`--test-limit 10`).

## Proximo passo

Repetir esta matriz com um recorte de eventos que garanta picks validos para a
RNC, antes da validacao da etapa `-e` no ambiente IAG/SEISAPP.
