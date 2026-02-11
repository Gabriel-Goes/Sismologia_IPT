# Operacao 0025 - Matriz sem -e com pre (10 eventos)

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `legado`  
**Status:** `concluida`  
**Fase:** `execucao-legado`  
**Tag:** `teste-execucao`

## Objetivo

Executar e depurar uma matriz local sem aquisicao (`-e`) incluindo
pre-processamento, para validar o comportamento integrado de:

1. `-pe` (pre-processamento)
2. `-pr` (predicao)
3. `-po` (pos-processamento)
4. `-m` (mapas)
5. `-r` (relatorio)

com `--test-limit 10`, tratando a investigacao como uma unica operacao.

## Comandos executados na mesma operacao

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh \
  --cases pre,predict,pos,maps,report \
  --test-limit 10
```

1. **Tentativa A (estado inicial da operacao):**
   - `archive_id=20260211_084132`
2. **Tentativa B (apos correcao de insumo):**
   - restauracao de `eventos.csv` completo a partir de
     `.specs/codebase/arquivos/eventos/.bkp/eventos.csv.20260210163707`
   - `archive_id=20260211_084816`

## Evidencias

### Tentativa A (`20260211_084132`) - diagnostico do problema

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

### Tentativa B (`20260211_084816`) - reteste com `eventos.csv` restaurado

1. Matriz consolidada:
   - [0025b-matriz-sem-e-com-pre-10.tsv](/anexos/anexo-0025b-matriz-sem-e-com-pre-10-tsv)
2. Contexto de execucao (ambientes/casos):
   - [0025b-manifest.env](/anexos/anexo-0025b-manifest-env)
3. Log da etapa `predict` (10 eventos):
   - [0025b-predict-10-eventos.log](/anexos/anexo-0025b-predict-10-eventos-log)
4. Log da etapa `pos` (com dados):
   - [0025b-pos-com-dados.log](/anexos/anexo-0025b-pos-com-dados-log)

## Resultado consolidado da operacao

1. `pre` -> `rc=0`
2. `predict` -> `rc=0`
3. `pos` -> `rc=0`
4. `maps` -> `rc=0`
5. `report` -> `rc=0`

## Interpretacao

1. A tentativa A mostrou que o fluxo estava tecnicamente estavel (`rc=0`), mas
   com insumo degradado:
   - `eventos.csv` vigente continha apenas cabecalho (1 linha).
   - `predict` retornou `0 eventos unicos selecionados (0 picks)`.
2. A tentativa B confirmou a causa-raiz ao restaurar `eventos.csv` completo:
   - `predict` passou para `10 eventos unicos selecionados (32 picks)`.
   - `pos` executou com dados reais (sem a mensagem de "sem picks validos").
3. Portanto, esta operacao valida duas propriedades:
   - o pipeline sem `-e` executa ponta a ponta;
   - a utilidade do resultado depende diretamente da qualidade do
     `eventos.csv` de entrada.

## Proximo passo

Repetir esta matriz com um recorte de eventos que garanta picks validos para a
RNC, antes da validacao da etapa `-e` no ambiente IAG/SEISAPP.
