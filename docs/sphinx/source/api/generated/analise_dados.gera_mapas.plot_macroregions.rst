analise\_dados.gera\_mapas.plot\_macroregions
=============================================

.. currentmodule:: analise_dados.gera_mapas

.. autofunction:: plot_macroregions

Resumo
------

Itera sobre as macroregioes de um ``GeoDataFrame`` e gera um mapa por regiao,
plotando os eventos sobre cada recorte geografico.

Parametros
----------

- ``gdf``: ``geopandas.GeoDataFrame`` com geometria e coluna ``nome`` da
  macroregiao.
- ``data``: ``pandas.DataFrame`` com coordenadas de eventos (``Latitude`` e
  ``Longitude``).

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Adiciona ``Longitude_jitter`` e ``Latitude_jitter`` em ``data``.
- Salva um PNG por macroregiao em ``arquivos/figuras/mapas/``.
- Cria e remove arquivo temporario para legenda durante a plotagem.

