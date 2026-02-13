Dois Objetivos
==============

Esta documentacao passa a operar com dois trilhos explicitos e complementares.

Trilho 1: Objetivo Da Codebase Legado
-------------------------------------

Pergunta central:

- O que o sistema legado faz hoje, em qual ordem, com quais dependencias?

Fontes principais:

- ``.specs/codebase/*.md``
- ``docs/sphinx/source/guia/*``
- ``docs/sphinx/source/api/*``
- ``docs/sphinx/source/artefatos/*``
- ``documentação/estado_atual_sistema.md``

Trilho 2: Objetivo Da Refatoracao
---------------------------------

Pergunta central:

- Como a refatoracao sera planejada, executada e validada?

Fontes principais:

- ``.specs/project/PROJECT.md``
- ``.specs/project/ROADMAP.md``
- ``.specs/project/STATE.md``
- ``docs/operacoes/*.md``
- ``docs/sphinx/source/operacoes/*.rst``

Regra Editorial
---------------

Cada registro de operacao deve indicar contexto explicito:

- ``Contexto: refatoracao``
- ``Contexto: legado``

Se uma mudanca cruzar os dois trilhos, priorizar separacao em dois commits e
dois registros para manter rastreabilidade limpa.

Continue A Leitura
------------------

- Se foco for entendimento do legado: :doc:`/guia/index`
- Se foco for historico da refatoracao: :doc:`/operacoes/index`
