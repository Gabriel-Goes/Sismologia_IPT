Execucoes De Teste Do Fluxo Legado
==================================

Objetivo
--------

Consolidar um roteiro reproduzivel para testar o ``fluxo_sismo.sh`` sem alterar
o legado, usando as evidencias ja levantadas nas operacoes:

- :doc:`/operacoes/0007-compreensao-comportamento-fluxo-sismo`
- :doc:`/operacoes/0008-preparacao-ambiente-pyenv-duplo`

Escopo do teste
---------------

- Script orquestrador: :doc:`/artefatos/fluxo-sismo-sh`
- Baseline testado: ``.specs/codebase/``
- Estrategia: execucao isolada por etapa (flags), nunca fluxo completo na
  primeira rodada.

Preflight minimo
----------------

1. Confirmar catalogo de entrada em ``.specs/codebase/arquivos/catalogo/``.
2. Confirmar ambiente Python ativo conforme etapa:
   - pipeline geral: ``PYENV_VERSION=sismo-core-311``
   - RNC legado: ``PYENV_VERSION=sismo-rnc-379``
3. Executar via runner isolado para evitar sujeira na branch:
   ``scripts/dev/run_fluxo_isolated.sh``.
4. Para matriz completa com arquivamento automatico de logs/resultados:
   ``scripts/dev/run_fluxo_test_matrix_archived.sh``.

Comandos base
-------------

Ajuda do runner:

.. code-block:: bash

   scripts/dev/run_fluxo_isolated.sh --help

Ajuda do runner de matriz com arquivamento:

.. code-block:: bash

   scripts/dev/run_fluxo_test_matrix_archived.sh --help

Teste de ajuda do pipeline (com catalogo):

.. code-block:: bash

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv --help

Teste por etapa (exemplos):

.. code-block:: bash

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -pe

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -e -t

   PYENV_VERSION=sismo-rnc-379 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -pr

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -po

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -m

   PYENV_VERSION=sismo-core-311 \
   scripts/dev/run_fluxo_isolated.sh -- catalogo_jul_filtrado.csv -r

Matriz automatica (arquivada no repositorio):

.. code-block:: bash

   scripts/dev/run_fluxo_test_matrix_archived.sh --test-limit 10

Por padrao, este comando arquiva logs e sumario em:

- ``.specs/codebase/arquivos/registros/test_matrix/<timestamp>/``

Matriz de leitura dos resultados
--------------------------------

.. list-table::
   :header-rows: 1

   * - Etapa
     - Flag
     - Resultado observado nas execucoes
     - Leitura tecnica
   * - Ajuda
     - ``--help``
     - Sem catalogo falha; com catalogo exibe ajuda.
     - Parse atual exige catalogo antes de opcoes.
   * - Pre-processamento
     - ``-pe``
     - Falha tipica por dependencia ausente (ex.: ``shapely``).
     - Contrato da etapa depende de stack geo completa.
   * - Aquisicao
     - ``-e -t``
     - Pode falhar por pasta de backup ausente e por libs (ex.: ``tqdm``).
     - Etapa sensivel a estrutura de diretorios + ambiente.
   * - Predicao (RNC)
     - ``-pr``
     - Falha tipica por TensorFlow ausente/incompativel.
     - Deve usar ambiente dedicado da RNC legado.
   * - Pos-processamento
     - ``-po``
     - Falha tipica por libs de analise (ex.: ``seaborn``).
     - Etapa de consolidacao depende do stack core completo.
   * - Mapas
     - ``-m``
     - Pode encerrar sem erro e sem gerar mapa.
     - Comportamento esperado quando ``df_nc_pos.csv`` nao existe.
   * - Relatorio
     - ``-r``
     - Scripts Python executam; ``pdflatex`` pode falhar.
     - Problemas aqui costumam ser de ambiente TeX/template.

Onde ler logs
-------------

- Log principal: ``.specs/codebase/arquivos/registros/Sismo_Pipeline.log``
- Backups: ``.specs/codebase/arquivos/registros/.bkp/``

Use este padrao para triagem rapida:

.. code-block:: bash

   tail -n 120 .specs/codebase/arquivos/registros/Sismo_Pipeline.log

Critério de sucesso desta fase
------------------------------

Nesta fase, sucesso nao significa "pipeline completo verde". Sucesso significa:

1. reproduzir comportamento por etapa;
2. identificar dependencias/contratos de cada fase;
3. transformar isso em insumo para a reescrita v2.

Proximo passo
-------------

- :doc:`/guia/scripts-de-encapsulamento`
- :doc:`/guia/fluxo-e-referencias`
- :doc:`/api/index`
- :doc:`/operacoes/0007-compreensao-comportamento-fluxo-sismo`
