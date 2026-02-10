Operacao 0020 - Contrato pr->po para cenarios sem dados
========================================================

Resumo
------

Correcao do contrato de dados entre predicao e pos-processamento para evitar
quebra quando ``predito.csv`` estiver vazio ou com schema parcial.

Efeito principal
----------------

- ``-po`` deixa de falhar por ``KeyError`` em ausencia de colunas de probabilidade;
- saidas vazias passam a ser geradas de forma explicita e rastreavel;
- reteste curto ``predict,pos`` concluiu com ``rc=0`` em ambos os casos.

Arquivos de interesse
---------------------

- :doc:`rnc.prediction.discrim </api/generated/rnc.prediction.discrim>`
- :doc:`analise_dados.pos_processa.main </api/generated/analise_dados.pos_processa.main>`
- :doc:`Matriz curta de validacao </anexos/anexo-0020-matriz-predict-pos-10-tsv>`
- :doc:`Log de pos-processamento sem dados </anexos/anexo-0020-pos-sem-dados-log>`

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0020-contrato-pr-po-sem-dados>`
