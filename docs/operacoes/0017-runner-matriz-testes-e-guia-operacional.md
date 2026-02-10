# Operacao 0017 - Runner de matriz de testes e guia operacional

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`

## Objetivo

Padronizar a execucao de testes do legado com arquivamento de evidencias no
repositorio e registrar o fluxo operacional no User Guide.

## Escopo executado

1. Criacao do runner dedicado de matriz com arquivamento:
   - `scripts/dev/run_fluxo_test_matrix_archived.sh`
2. Correcao do runner para evitar copiar logs antigos para novos arquivos de
   arquivamento:
   - limpeza de `arquivos/registros/test_matrix` no `run_dir` antes da execucao.
3. Inclusao de guia de testes no Sphinx:
   - `docs/sphinx/source/guia/execucoes-de-teste-fluxo-legado.rst`
   - navegacao atualizada em:
     - `docs/sphinx/source/guia/index.rst`
     - `docs/sphinx/source/guia/fluxo-e-referencias.rst`
4. Registro de memoria de ambiente pyenv/virtualenv para operacao local:
   - `documentação/memoria_ambiente_pyenv_virtualenv.md`
   - referencia adicionada em `documentação/README.md`
5. Definicao do Python padrao do repositorio:
   - `.python-version` com `sismo-core-311`

## Resultado

1. A matriz de testes pode ser executada e arquivada com um comando:
   - `scripts/dev/run_fluxo_test_matrix_archived.sh --test-limit 10`
2. O risco de poluicao entre execucoes sucessivas foi reduzido.
3. O User Guide passou a ter uma pagina dedicada para execucao de testes do
   legado, com comandos e leitura de resultados.
4. A ativacao do ambiente Python core ficou explicita na raiz do projeto.

## Observacoes

1. Esta operacao nao comita artefatos runtime de `arquivos/eventos/*` e
   `arquivos/registros/*` alterados por execucoes locais.
2. Evidencias de teste devem ser mantidas preferencialmente em `docs/operacoes/anexos/`
   ou em pastas de arquivamento deliberadas.

## Proximo passo

Executar a matriz com `--test-limit 10` no ambiente-alvo (IAG/SEISAPP) e
registrar os resultados como nova operacao.
