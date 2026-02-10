Operacao 0018 - Validacao do runner de matriz com 10 eventos
=============================================================

Resumo
------

Validacao pratica do runner de matriz introduzido na operacao 0017, com
execucao real em ``--test-limit 10`` e arquivamento de evidencias.

Efeito principal
----------------

- confirmacao de que nao ha mais copia de logs antigos no novo ``archive_id``;
- consolidacao do estado atual das etapas do legado fora do ambiente IAG;
- registro formal da falha atual de ``-po`` por ausencia de ``Pick Prob_Nat``.

Arquivos de interesse
---------------------

- ``docs/operacoes/anexos/0018-matriz-testes-fluxo-sismo-10.tsv``
- ``docs/operacoes/anexos/0018-falha-pos-pick-prob-nat.log``
- ``.specs/codebase/arquivos/registros/test_matrix/20260210_170316/``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0018-validacao-runner-matriz-10-eventos>`
- :download:`Matriz 10 eventos (TSV) <../../../operacoes/anexos/0018-matriz-testes-fluxo-sismo-10.tsv>`
- :download:`Falha pos_processa (log) <../../../operacoes/anexos/0018-falha-pos-pick-prob-nat.log>`
