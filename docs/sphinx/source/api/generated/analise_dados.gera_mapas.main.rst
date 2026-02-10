analise_dados.gera_mapas.main
=============================

.. currentmodule:: analise_dados.gera_mapas

.. autofunction:: main

Resumo
------

Entrypoint da etapa de mapas. Carrega dados pos-processados e produz mapas
geograficos de distribuicao/probabilidade usados na leitura tecnica e no
relatorio final.

Parametros
----------

Esta funcao nao recebe argumentos explicitos; opera nos caminhos padrao do
pipeline.

Retorno
-------

Retorna dataframe utilizado para geracao dos mapas.

Efeitos colaterais
------------------

- Salva mapas e figuras em ``arquivos/figuras/mapas/``.
