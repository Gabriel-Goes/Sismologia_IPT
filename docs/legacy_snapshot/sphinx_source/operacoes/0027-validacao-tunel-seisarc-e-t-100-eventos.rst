Operacao 0027 - Validacao de aquisicao via tunel (SEISARC) com ``-e -t`` (100 eventos)
=========================================================================================

Resumo
------

Validacao de aquisicao de eventos no fluxo legado usando tunel reverso SEISAPP ->
GeoServer, com endpoint local ``http://127.0.0.1:18080`` e lote de 100 eventos no
modo de teste.

Efeito principal
----------------

- adiciona fallback operacional do tunel no ``fluxo_eventos.py``;
- consolida default de ``TEST_EVENT_LIMIT=100`` para ``-t``;
- confirma que ``-e -t`` conclui com sucesso usando o tunel.

Arquivos de interesse
---------------------

- :doc:`Source de fluxo_eventos.py </_modules/nucleo/fluxo_eventos>`
- :doc:`Artefato fluxo_sismo.sh </artefatos/fluxo-sismo-sh>`
- :doc:`Documento detalhado </detalhes/0027-validacao-tunel-seisarc-e-t-100-eventos>`

