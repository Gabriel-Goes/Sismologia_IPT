Operacao 0025 - Matriz sem -e com pre (10 eventos)
===================================================

Resumo
------

Validacao e depuracao local da cadeia ``pre -> predict -> pos -> maps ->
report`` sem executar aquisicao (``-e``), com ``--test-limit 10``, em tres
tentativas dentro da mesma operacao.

Efeito principal
----------------

- confirmacao de ``rc=0`` em todas as etapas da matriz sem ``-e``;
- identificacao de causa-raiz para ``predict`` com ``0 eventos``;
- confirmacao de processamento real apos restauracao de ``eventos.csv``.
- validacao final de comportamento com falha em ``-e`` sem corromper
  ``eventos.csv``.

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
- Tentativa C (falha controlada de ``-e`` + reteste ``-pr``):
  :doc:`Resumo do todos </anexos/anexo-0025c-summary-todos-tsv>`,
  :doc:`Log falha em e </anexos/anexo-0025c-todos-falha-e-log>`,
  :doc:`Integridade do eventos.csv </anexos/anexo-0025c-eventos-integridade-txt>`,
  :doc:`Tabela final de predito </anexos/anexo-0025c-predito-csv>`.

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0025-matriz-sem-e-com-pre-10-eventos>`
