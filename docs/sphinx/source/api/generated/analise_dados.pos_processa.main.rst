analise_dados.pos_processa.main
===============================

.. currentmodule:: analise_dados.pos_processa

.. autofunction:: main

Resumo
------

Entrypoint do pos-processamento legado. Consolida resultados de classificacao,
calcula metricas por evento/periodo e produz tabelas/graficos para analise
final e para o relatorio.

Parametros
----------

Esta funcao nao recebe argumentos explicitos; usa caminhos padrao do pipeline.

Retorno
-------

Retorna dataframes consolidados do fluxo pos-processado.

Efeitos colaterais
------------------

- Atualiza artefatos em ``arquivos/resultados/``.
- Gera figuras em ``arquivos/figuras/pos_process/``.
