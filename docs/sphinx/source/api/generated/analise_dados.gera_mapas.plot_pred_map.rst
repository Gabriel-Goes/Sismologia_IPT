analise\_dados.gera\_mapas.plot\_pred\_map
==========================================

.. currentmodule:: analise_dados.gera_mapas

.. autofunction:: plot_pred_map

Resumo
------

Gera um mapa de eventos com PyGMT usando as colunas de latitude/longitude e
colore cada ponto pela probabilidade de evento natural (``Event Prob_Nat``).

Parametros
----------

- ``data``: ``pandas.DataFrame`` com, no minimo, ``Latitude``, ``Longitude`` e
  ``Event Prob_Nat``.
- ``filename``: nome do arquivo de saida (salvo em
  ``arquivos/figuras/mapas/``).

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Adiciona as colunas ``Longitude_jitter`` e ``Latitude_jitter`` em ``data``.
- Salva figura em ``arquivos/figuras/mapas/{filename}``.
- Exibe a figura com ``fig.show()``.

