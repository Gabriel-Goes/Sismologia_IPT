nucleo.fluxo\_eventos.iterar\_eventos
=====================================

.. currentmodule:: nucleo.fluxo_eventos

.. autofunction:: iterar_eventos

Resumo
------

Percorre eventos do catalogo, filtra picks de fase ``P``, consulta metadados de
estacao, baixa formas de onda e grava os CSVs de eventos validos e erros.

Parametros
----------

- ``eventos``: lista de eventos ObsPy.
- ``data_client``: cliente FDSN primario.
- ``data_client_bkp``: cliente FDSN de backup.
- ``baixar``: se ``True``, tenta baixar forma de onda e salvar ``.mseed``.
- ``random``: parametro legado; nao controla a aleatoriedade atual do offset.

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Salva ``.mseed`` em ``arquivos/mseed/{EVENT}/``.
- Gera ``arquivos/eventos/eventos.csv``.
- Gera ``arquivos/eventos/erros.csv``.
- Emite logs extensos de progresso e erro no stdout.

