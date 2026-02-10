Visao Geral
===========

Objetivo
--------

Reescrever o fluxo do projeto de classificacao sismologica com arquitetura mais
limpa, modular e auditavel, mantendo rastreabilidade tecnica para avaliacao
academica.

Estrutura de trabalho
---------------------

- ``.specs/codebase/``: baseline legado (fonte de consulta).
- ``.specs/project/``: planejamento e memoria de execucao.
- ``docs/operacoes/``: diario de operacoes por commit.
- ``docs/sphinx/``: publicacao da documentacao via GitHub Pages.
- ``docs/sphinx/source/guia/``: user guide com links para API.
- ``docs/sphinx/source/api/``: referencia de funcoes e classes.
- ``docs/sphinx/source/artefatos/``: scripts e arquivos txt renderizados.

Fluxo Legado (fluxo_sismo.sh)
-----------------------------

O orquestrador do legado e ``.specs/codebase/fluxo_sismo.sh``. Ele conecta
todo o ciclo: catalogo -> aquisicao -> classificacao -> analise -> mapas ->
relatorio.

Entrada e controle
------------------

- Entrada principal: arquivo de catalogo em ``.specs/codebase/arquivos/catalogo/``.
- Flags de controle:
  - ``--pre``: tratamento de catalogo
  - ``--eventos``: aquisicao de eventos e formas de onda
  - ``--predict``: inferencia da RNC
  - ``--pos``: pos-processamento e metricas
  - ``--maps``: geracao de mapas
  - ``--report``: geracao de relatorio PDF
  - ``--test``: modo de teste para aquisicao
- Log central: ``.specs/codebase/arquivos/registros/Sismo_Pipeline.log`` (com backup automatico).

Ordem de execucao e scripts chamados
------------------------------------

1. Tratamento do catalogo (`--pre`)
   Script: ``.specs/codebase/fonte/analise_dados/pre_processa.py``
   Objetivo: filtrar/tratar catalogo de entrada.

2. Aquisicao de eventos (`--eventos`)
   Script: ``.specs/codebase/fonte/nucleo/fluxo_eventos.py``
   Objetivo: consultar FDSN, baixar formas de onda e gerar ``eventos.csv``.

3. Predicao (`--predict`)
   Script: ``.specs/codebase/fonte/rnc/run.py``
   Cadeia interna: ``data_process.py`` -> ``prediction.py``
   Objetivo: extrair espectrogramas e classificar picks/eventos.

4. Pos-processamento (`--pos`)
   Script: ``.specs/codebase/fonte/analise_dados/pos_processa.py``
   Objetivo: consolidar metricas, filtros e graficos.

5. Mapas (`--maps`)
   Script: ``.specs/codebase/fonte/analise_dados/gera_mapas.py``
   Objetivo: produzir mapas de distribuicao/probabilidade.

6. Relatorio (`--report`)
   Scripts: ``figures.py`` e ``mapa.py`` em
   ``.specs/codebase/fonte/relatorio-sismologia/pyscripts/``
   Finalizacao: ``pdflatex`` em ``relatorio_preditivo.tex``.

Artefatos principais por etapa
------------------------------

- Eventos: ``.specs/codebase/arquivos/eventos/eventos.csv``
- Erros de aquisicao/pipeline: ``.specs/codebase/arquivos/eventos/erros.csv``
- Predicao: ``.specs/codebase/arquivos/resultados/predito.csv``
- Pos-processamento: ``.specs/codebase/arquivos/resultados/*analisado*.csv``
- Relatorio final: ``.specs/codebase/arquivos/resultados/relatorios/*.pdf``

Dependencias-chave do fluxo
---------------------------

- Aquisicao sismologica: ``obspy``
- Inferencia CNN: ``tensorflow``, ``numpy``, ``pandas``
- Analise/plots: ``pandas``, ``matplotlib``, ``seaborn``
- Geo/mapas: ``geopandas``, ``shapely``, ``pygmt``
- Relatorio: ``pdflatex``

Diretriz de execucao
--------------------

Cada operacao relevante deve:

1. gerar alteracoes pequenas e verificaveis;
2. ser registrada em arquivo de operacao;
3. ser commitada isoladamente.

Publicacao
----------

A documentacao HTML e gerada com Sphinx e publicada no GitHub Pages por
workflow automatizado.
