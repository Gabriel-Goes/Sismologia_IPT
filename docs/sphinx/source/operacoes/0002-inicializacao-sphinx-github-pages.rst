Operacao 0002 - Inicializacao Sphinx + GitHub Pages
====================================================

Resumo
------

Criada a base de documentacao navegavel da refatoracao com:

- estrutura Sphinx em ``docs/sphinx/``;
- indice de operacoes;
- workflow para publicacao no GitHub Pages.

Entregas
--------

- ``docs/sphinx/source/index.rst``
- ``docs/sphinx/source/visao_geral.rst``
- ``docs/sphinx/source/operacoes/index.rst``
- ``.github/workflows/docs.yml``

Build local
-----------

Comandos:

.. code-block:: bash

   sphinx-build -b html docs/sphinx/source docs/sphinx/build/html

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0002-inicializacao-sphinx-github-pages>`
