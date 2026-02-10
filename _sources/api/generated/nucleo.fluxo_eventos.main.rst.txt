nucleo.fluxo\_eventos.main
==========================

.. currentmodule:: nucleo.fluxo_eventos

.. autofunction:: main

Resumo
------

Ponto de entrada programatico do modulo de fluxo: cria clientes FDSN,
configura fallback e executa ``fluxo_eventos``.

Parametros
----------

- ``EventIDs``: lista de identificadores de evento.

Retorno
-------

Retorna ``(catalogo, missin_ids)`` vindo de ``fluxo_eventos``.

Observacao
----------

Os endpoints sao fixos no codigo legado:

- primario: ``http://10.110.1.132:18003``
- backup: ``http://rsbr.on.br:8081``

