Operacao 0025 - Matriz sem -e com pre (10 eventos)
===================================================

Resumo
------

Validacao e depuracao local da cadeia ``pre -> predict -> pos -> maps ->
report`` sem executar aquisicao (``-e``), com ``--test-limit 10``, em duas
tentativas dentro da mesma operacao.

Efeito principal
----------------

- confirmacao de ``rc=0`` em todas as etapas da matriz sem ``-e``;
- identificacao de causa-raiz para ``predict`` com ``0 eventos``;
- confirmacao de processamento real apos restauracao de ``eventos.csv``.

Arquivos de interesse
---------------------

- Tentativa A (diagnostico):
  :doc:`Matriz </anexos/anexo-0025-matriz-sem-e-com-pre-10-tsv>`,
  :doc:`Predict 0 eventos </anexos/anexo-0025-predict-0-eventos-log>`,
  :doc:`Pos sem picks </anexos/anexo-0025-pos-sem-picks-log>`.
- Tentativa B (apos restaurar ``eventos.csv``):
  :doc:`Matriz </anexos/anexo-0025b-matriz-sem-e-com-pre-10-tsv>`,
  :doc:`Predict 10 eventos </anexos/anexo-0025b-predict-10-eventos-log>`,
  :doc:`Pos com dados </anexos/anexo-0025b-pos-com-dados-log>`.

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0025-matriz-sem-e-com-pre-10-eventos>`
