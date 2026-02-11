Operacao 0025 - Matriz sem -e com pre (10 eventos)
===================================================

Resumo
------

Validacao local da cadeia ``pre -> predict -> pos -> maps -> report`` sem
executar aquisicao (``-e``), com ``--test-limit 10``.

Efeito principal
----------------

- confirmacao de ``rc=0`` em todas as etapas da matriz sem ``-e``;
- confirmacao de que ``predict`` segue com ``0 eventos`` no recorte atual;
- consolidacao de que ``pos`` trata entrada vazia sem quebrar o fluxo.

Arquivos de interesse
---------------------

- :doc:`Matriz consolidada (anexo) </anexos/anexo-0025-matriz-sem-e-com-pre-10-tsv>`
- :doc:`Manifest da execucao (anexo) </anexos/anexo-0025-manifest-env>`
- :doc:`Log do pre-processamento (anexo) </anexos/anexo-0025-pre-10-log>`
- :doc:`Log da predicao (0 eventos) </anexos/anexo-0025-predict-0-eventos-log>`
- :doc:`Log do pos-processamento (sem picks) </anexos/anexo-0025-pos-sem-picks-log>`

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0025-matriz-sem-e-com-pre-10-eventos>`
