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
3. **Tentativa C (validacao definitiva do comportamento com falha em `-e`):**
   - execucao completa:

```bash
scripts/dev/run_fluxo_test_matrix_archived.sh --cases todos --test-limit 10 --keep-run-dir
```

   - `archive_id=20260211_092006` (`todos` retorna `rc=1` por falha de FDSN)
   - reteste de `-pr` no mesmo `run_dir`, usando `eventos.csv` existente:

```bash
cd /tmp/classificador-matrix-3i2BZ6
env TEST_EVENT_LIMIT=10 PYENV_VERSION=sismo-core-311 RNC_PYENV_VERSION=sismo-rnc-379 \
  bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -pr -t
```

   - resultado do reteste: `rc=0`, `10 eventos`, `32 picks`, `28 picks processados`.

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

### Tentativa C (`20260211_092006` + reteste `-pr`) - validacao final

1. Matriz completa (`todos`) com falha esperada em `-e`:
   - [0025c-summary-todos.tsv](/anexos/anexo-0025c-summary-todos-tsv)
   - [0025c-todos-falha-e.log](/anexos/anexo-0025c-todos-falha-e-log)
2. Integridade do `eventos.csv` preservada:
   - [0025c-eventos-integridade.txt](/anexos/anexo-0025c-eventos-integridade-txt)
3. Reteste `-pr -t` no mesmo `run_dir`:
   - [0025c-predict-after-eventos-fail.log](/anexos/anexo-0025c-predict-after-eventos-fail-log)
4. Tabelas de resultado (artefatos principais):
   - [0025c-predito.csv](/anexos/anexo-0025c-predito-csv)
   - [0025c-pre_processado.csv](/anexos/anexo-0025c-pre-processado-csv)
   - [0025c-erros.csv](/anexos/anexo-0025c-erros-csv)
   - [0025c-catalogo_jul_filtrado_filtrado.csv](/anexos/anexo-0025c-catalogo-jul-filtrado-filtrado-csv)

## Resultado tabular consolidado da tentativa C

| Event | Picks selecionados | Picks processados | Erros | Descartados |
| --- | ---: | ---: | ---: | ---: |
| 20150317T190704 | 3 | 2 | 1 | 1 |
| 20150923T124902 | 5 | 5 | 0 | 0 |
| 20160111T033106 | 5 | 2 | 3 | 3 |
| 20170405T233728 | 2 | 2 | 0 | 0 |
| 20190514T063803 | 2 | 2 | 0 | 0 |
| 20190830T014731 | 3 | 3 | 0 | 0 |
| 20200717T144815 | 2 | 2 | 0 | 0 |
| 20200910T062943 | 2 | 2 | 0 | 0 |
| 20220328T072623 | 4 | 4 | 0 | 0 |
| 20230524T184558 | 4 | 4 | 0 | 0 |
| **TOTAL** | **32** | **28** | **4** | **4** |

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
4. A tentativa C adiciona a validacao comportamental do fluxo completo:
   - no comando unico `-pe -e -pr -po -m -r -t`, a falha de `-e` interrompe o
     restante por `set -e` (nao chega em `-pr`);
   - mesmo com essa falha, `eventos.csv` nao foi sobrescrito com cabecalho
     vazio;
   - ao rodar `-pr -t` separadamente no mesmo contexto, o pipeline usa o
     `eventos.csv` existente e produz os artefatos de predicao esperados.

## Proximo passo

Levar a validacao da etapa `-e` para o ambiente IAG/SEISAPP (com acesso ao
SeisComP/event), mantendo o mesmo protocolo de evidencias.
