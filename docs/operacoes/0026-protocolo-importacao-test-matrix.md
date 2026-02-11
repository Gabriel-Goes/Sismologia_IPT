# Operacao 0026 - Protocolo de importacao test_matrix para documentacao

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`  
**Fase:** `execucao-legado`  
**Tag:** `hardening-ambiente`

## Objetivo

Separar explicitamente:

1. operacoes de teste de codigo (ex.: `0025`);
2. operacoes de evolucao de protocolo/ferramenta de documentacao.

Nesta operacao, foi criado um script dedicado para importar artefatos de
`test_matrix` para a documentacao Sphinx, padronizando o processo.

## Mudanca implementada

Novo script:

- `scripts/dev/import_test_matrix_to_docs.sh`

Capacidades:

1. importa anexos a partir de uma execucao em
   `.specs/codebase/arquivos/registros/test_matrix/<archive_id>`;
2. copia os arquivos para `docs/operacoes/anexos/` com prefixo de operacao;
3. cria/atualiza paginas em `docs/sphinx/source/anexos/anexo-*.rst`;
4. atualiza automaticamente `docs/sphinx/source/anexos/index.rst` sem duplicar
   entradas.

## Validacao da automacao

Comando executado:

```bash
scripts/dev/import_test_matrix_to_docs.sh \
  --archive-id 20260211_085515 \
  --op-tag 0026a \
  --files summary,manifest,predict,pre_processado,predito,analisado_final,erros
```

Resultado:

1. `itens ok: 7`
2. `itens skip: 0`
3. anexos renderizados criados no Sphinx para a operacao `0026a`.

## Evidencias importadas (0026a)

1. [0026a-summary.tsv](/anexos/anexo-0026a-summary-tsv)
2. [0026a-manifest.env](/anexos/anexo-0026a-manifest-env)
3. [0026a-predict.log](/anexos/anexo-0026a-predict-log)
4. [0026a-pre_processado.csv](/anexos/anexo-0026a-pre-processado-csv)
5. [0026a-predito.csv](/anexos/anexo-0026a-predito-csv)
6. [0026a-analisado_final.csv](/anexos/anexo-0026a-analisado-final-csv)
7. [0026a-erros.csv](/anexos/anexo-0026a-erros-csv)

## Resultado

1. `0025` permanece focada em teste e diagnostico de execucao.
2. A mudanca de comportamento/protocolo ficou isolada em `0026`.
3. O fluxo de publicacao de evidencias passou a ser reproduzivel por script.

## Proximo passo

Usar o script como procedimento padrao ao final de cada nova matriz relevante de
teste, evitando importacao manual de anexos.
