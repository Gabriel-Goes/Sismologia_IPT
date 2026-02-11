Operacao 0022 - Diagnostico do Dependabot no ambiente RNC legado
=================================================================

Resumo
------

Diagnostico de compatibilidade dos bumps do Dependabot no arquivo de
requirements legado da RNC, com foco em reproducibilidade do ambiente
``sismo-rnc-379`` (Python 3.7.9).
O contexto desta operacao e a resposta tecnica aos alertas criticos de
seguranca reportados pelo Dependabot.

Efeito principal
----------------

- confirmacao de incompatibilidades diretas com Python 3.7;
- confirmacao de conflitos internos de pins (TensorFlow, Protobuf e Estimator);
- decisao de manter pins legados na trilha de refatoracao ate separar
  requirements por trilha.

Arquivos de interesse
---------------------

- :doc:`Requirements RNC legado </artefatos/requirements-rnc-legacy-txt>`
- :doc:`Memoria de compatibilidade Dependabot x RNC </artefatos/memoria-dependabot-rnc-compatibilidade-md>`

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0022-diagnostico-dependabot-ambiente-rnc-legado>`
