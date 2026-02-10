analise_dados.pre_processa.main
================================

.. currentmodule:: analise_dados.pre_processa

.. autofunction:: main

Resumo
------

Entrypoint do pre-processamento legado. Carrega catalogo/eventos de entrada,
normaliza colunas e datas, aplica filtros espaciais (Brasil) e gera saidas
filtradas para o restante do pipeline.

Parametros
----------

- ``args``: namespace de argumentos CLI (catalogo/eventos, flags de mapa e teste).

Retorno
-------

Retorna ``catalogo`` tratado quando a entrada e catalogo; caso contrario,
retorna ``None`` quando nao ha entrada valida.

Efeitos colaterais
------------------

- Escreve ``arquivos/catalogo/*_filtrado.csv``.
- Gera figuras em ``arquivos/figuras/pre_processa/``.
- Pode gerar mapa de distribuicao conforme flags.
