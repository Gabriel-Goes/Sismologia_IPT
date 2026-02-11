Visao Geral
===========

Objetivo
--------

Reescrever o fluxo do projeto de classificacao sismologica com arquitetura mais
limpa, modular e auditavel, mantendo rastreabilidade tecnica para avaliacao
academica.

Dois Trilhos
------------

Esta documentacao trabalha com dois objetivos em paralelo:

1. **Legado:** o que a codebase atual executa e como executa.
2. **Refatoracao:** como o v2 sera planejado, implementado e validado.

Detalhamento: :doc:`/dois_objetivos`

Estrutura de trabalho
---------------------

- ``.specs/codebase/``: baseline legado (fonte de consulta).
- ``.specs/project/``: planejamento e memoria de execucao.
- ``docs/operacoes/``: diario de operacoes por commit.
- ``docs/sphinx/``: publicacao da documentacao via GitHub Pages.
- ``docs/sphinx/source/guia/``: user guide com links para API.
- ``docs/sphinx/source/api/``: referencia de funcoes e classes.
- ``docs/sphinx/source/artefatos/``: scripts e arquivos txt renderizados.

Trilho Legado: Fluxo Atual Da Codebase
--------------------------------------

Orquestrador principal:

- :doc:`fluxo_sismo.sh </artefatos/fluxo-sismo-sh>`

Este orquestrador conecta o ciclo completo:
catalogo -> aquisicao -> classificacao -> analise -> mapas -> relatorio.

Entrada e controle
^^^^^^^^^^^^^^^^^^

- **Entrada principal:** catalogos em ``.specs/codebase/arquivos/catalogo/``.
- **Flags de controle:**

  - ``--pre``: tratamento de catalogo.
  - ``--eventos``: aquisicao de eventos e formas de onda.
  - ``--predict``: inferencia da RNC.
  - ``--pos``: pos-processamento e metricas.
  - ``--maps``: geracao de mapas.
  - ``--report``: geracao de relatorio PDF.
  - ``--test``: modo de teste para aquisicao.

- **Log central:** ``.specs/codebase/arquivos/registros/Sismo_Pipeline.log``.

Ordem de execucao e scripts chamados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Tratamento do catalogo** (``--pre``)

   - **Script (source):**
     `analise_dados/pre_processa.py <_modules/analise_dados/pre_processa.html#main>`_
   - **Docs:** :doc:`analise_dados.pre_processa.main </api/generated/analise_dados.pre_processa.main>`
   - **Objetivo:** filtrar/tratar catalogo de entrada.

2. **Aquisicao de eventos** (``--eventos``)

   - **Script (source):**
     `nucleo/fluxo_eventos.py <_modules/nucleo/fluxo_eventos.html#fluxo_eventos>`_
   - **Funcoes documentadas:**
     :doc:`nucleo.fluxo_eventos.fluxo_eventos </api/generated/nucleo.fluxo_eventos.fluxo_eventos>`,
     :doc:`nucleo.fluxo_eventos.iterar_eventos </api/generated/nucleo.fluxo_eventos.iterar_eventos>`,
     :doc:`nucleo.utils.csv2list </api/generated/nucleo.utils.csv2list>`.
   - **Objetivo:** consultar FDSN, baixar formas de onda e gerar ``eventos.csv``.

3. **Predicao** (``--predict``)

   - **Script (source):** `rnc/run.py <_modules/rnc/run.html#main>`_
   - **Docs:** :doc:`rnc.run.main </api/generated/rnc.run.main>`
   - **Funcoes documentadas:**
     :doc:`rnc.data_process.spectro_extract </api/generated/rnc.data_process.spectro_extract>`,
     :doc:`rnc.prediction.discrim </api/generated/rnc.prediction.discrim>`.
   - **Objetivo:** extrair espectrogramas e classificar picks/eventos.

4. **Pos-processamento** (``--pos``)

   - **Script (source):**
     `analise_dados/pos_processa.py <_modules/analise_dados/pos_processa.html#main>`_
   - **Docs:** :doc:`analise_dados.pos_processa.main </api/generated/analise_dados.pos_processa.main>`
   - **Funcoes documentadas:**
     :doc:`analise_dados.pos_processa.clean_data </api/generated/analise_dados.pos_processa.clean_data>`,
     :doc:`analise_dados.pos_processa.recall_event </api/generated/analise_dados.pos_processa.recall_event>`.
   - **Objetivo:** consolidar metricas, filtros e graficos.

5. **Mapas** (``--maps``)

   - **Script (source):**
     `analise_dados/gera_mapas.py <_modules/analise_dados/gera_mapas.html#main>`_
   - **Docs:** :doc:`analise_dados.gera_mapas.main </api/generated/analise_dados.gera_mapas.main>`
   - **Funcoes documentadas:**
     :doc:`analise_dados.gera_mapas.plot_pred_map </api/generated/analise_dados.gera_mapas.plot_pred_map>`,
     :doc:`analise_dados.gera_mapas.plot_macroregions </api/generated/analise_dados.gera_mapas.plot_macroregions>`.
   - **Objetivo:** produzir mapas de distribuicao/probabilidade.

6. **Relatorio** (``--report``)

   - **Scripts (source):**
     `figures.py <_modules/figures.html#generate_latex_for_figures>`_ e
     `mapa.py <_modules/mapa.html#generate_map_latex>`_.
   - **Docs:** :doc:`figures.generate_latex_for_figures </api/generated/figures.generate_latex_for_figures>`
     e :doc:`mapa.generate_map_latex </api/generated/mapa.generate_map_latex>`.
   - **Template final:** :doc:`relatorio_preditivo.tex </artefatos/relatorio-preditivo-tex>`.
   - **Objetivo:** gerar artefatos graficos e compilar PDF com ``pdflatex``.

Artefatos principais por etapa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Eventos:** ``.specs/codebase/arquivos/eventos/eventos.csv``.
- **Erros de aquisicao/pipeline:** ``.specs/codebase/arquivos/eventos/erros.csv``.
- **Predicao:** ``.specs/codebase/arquivos/resultados/predito.csv``.
- **Pos-processamento:** ``.specs/codebase/arquivos/resultados/*analisado*.csv``.
- **Relatorio final:** ``.specs/codebase/arquivos/resultados/relatorios/*.pdf``.

Dependencias-chave do fluxo
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Aquisicao sismologica:** ``obspy``.
- **Inferencia CNN:** ``tensorflow``, ``numpy``, ``pandas``.
- **Analise/plots:** ``pandas``, ``matplotlib``, ``seaborn``.
- **Geo/mapas:** ``geopandas``, ``shapely``, ``pygmt``.
- **Relatorio:** ``pdflatex``.

Trilho Refatoracao: Execucao Do V2
----------------------------------

Diretrizes de execucao incremental
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cada operacao relevante deve:

1. gerar alteracoes pequenas e verificaveis;
2. ser registrada em arquivo de operacao;
3. ser commitada isoladamente.

Publicacao da documentacao
^^^^^^^^^^^^^^^^^^^^^^^^^^

A documentacao HTML e gerada com Sphinx e publicada no GitHub Pages por
workflow automatizado.

Continue A Leitura
------------------

Proximo passo recomendado:

- :doc:`Dois Objetivos </dois_objetivos>`

Atalhos:

- :doc:`User Guide </guia/index>`
- :doc:`API Reference </api/index>`
- :doc:`Operacoes </operacoes/index>`
