nucleo.utils.csv2list
=====================

Resumo
------

Le um catalogo em ``arquivos/catalogo/`` e extrai a lista de ``EventID``
(primeira coluna separada por ``|``).

Parametros
----------

- ``csv_file``: nome do arquivo de catalogo.
- ``data``: filtro opcional por ano (comparacao com trecho do ``EventID``).

Retorno
-------

Lista de ``EventID``.

Observacao
----------

Quando ``data`` e informado, o filtro usa ``evid[3:7]`` para comparacao
numerica com o valor passado.

.. currentmodule:: nucleo.utils

.. autofunction:: csv2list
