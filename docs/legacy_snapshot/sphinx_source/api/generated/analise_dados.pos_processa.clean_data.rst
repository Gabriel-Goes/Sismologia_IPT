analise\_dados.pos\_processa.clean\_data
========================================

.. currentmodule:: analise_dados.pos_processa

.. autofunction:: clean_data

Resumo
------

Filtra e organiza eventos classificados como antropogenicos, criando subconjuntos
por faixas de probabilidade ``Event Prob_Ant`` para analise posterior.

Parametros
----------

- ``df``: ``pandas.DataFrame`` indexado por evento/pick com colunas de
  probabilidade e atributos de evento.

Retorno
-------

Retorna 6 ``DataFrame`` nesta ordem:

- ``events_Ant``: todos os eventos com ``Event Prob_Nat < 0.5``.
- ``events_Ant_90``: ``Event Prob_Ant >= 0.9``.
- ``events_Ant_80``: ``0.8 <= Event Prob_Ant < 0.9``.
- ``events_Ant_70``: ``0.7 <= Event Prob_Ant < 0.8``.
- ``events_Ant_65``: ``0.65 <= Event Prob_Ant < 0.7``.
- ``events_Ant_60``: ``0.6 <= Event Prob_Ant < 0.65``.

