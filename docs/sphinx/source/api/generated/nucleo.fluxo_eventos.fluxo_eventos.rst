nucleo.fluxo\_eventos.fluxo\_eventos
====================================

.. currentmodule:: nucleo.fluxo_eventos

.. autofunction:: fluxo_eventos

Resumo
------

Orquestra a aquisicao de eventos por ``EventID`` em cliente primario/backup,
chama ``iterar_eventos`` para processar picks e registra IDs ausentes.

Parametros
----------

- ``EventIDs``: lista de identificadores de evento.
- ``DATA_CLIENT``: cliente FDSN primario.
- ``DATA_CLIENT_BKP``: cliente FDSN secundario.

Retorno
-------

Retorna uma tupla ``(catalogo, ids_faltantes)``:

- ``catalogo``: ``obspy.core.event.Catalog`` com eventos encontrados.
- ``ids_faltantes``: lista de IDs nao encontrados nos servidores consultados.

Efeitos colaterais
------------------

- Dispara o processamento completo de picks via ``iterar_eventos``.
- Salva ``arquivos/registros/id_faltantes.csv``.

