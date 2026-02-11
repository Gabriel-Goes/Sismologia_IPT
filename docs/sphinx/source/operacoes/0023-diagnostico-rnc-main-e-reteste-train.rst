Operacao 0023 - Diagnostico da RNC pos-merge Dependabot e reteste do train.py
===============================================================================

Resumo
------

Consolidacao tecnica do estado da RNC apos merge de dependencias no ``main``,
incluindo reteste de ``train.py`` com ``analisado.csv`` presente e mapeamento
dos bloqueios reais de stack e schema.
A trilha em Python 3.11 e tratada como etapa de migracao controlada para
responder aos alertas criticos de seguranca do Dependabot, sem descontinuar
abruptamente a trilha legada.

Efeito principal
----------------

- confirmacao de que os pins do ``main`` nao fecham em trilha legada nem em
  trilha Python 3.11 como arquivo unico;
- confirmacao de falhas objetivas de ``train.py`` em ambos ambientes testados;
- definicao de proximo incremento: ``requirements-rnc-modern.txt`` minimo e
  validado.

Arquivos de interesse
---------------------

- :doc:`Compatibilidade do requirements do main </anexos/anexo-0023-requirements-main-compat-log>`
- :doc:`Reteste train legado (log) </anexos/anexo-0023-train-legacy-379-log>`
- :doc:`Reteste train moderno (log) </anexos/anexo-0023-train-modern-311-log>`
- :doc:`Checagem de schema do analisado.csv </anexos/anexo-0023-analisado-schema-check-log>`

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0023-diagnostico-rnc-main-e-reteste-train>`
