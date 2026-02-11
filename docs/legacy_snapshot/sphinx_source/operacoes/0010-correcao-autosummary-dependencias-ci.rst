Operacao 0010 - Correcao do autosummary no CI de documentacao
==============================================================

Resumo
------

Correcao de falha no GitHub Actions causada por import de dependencias Python
nao instaladas no runner durante a geracao de paginas de API com autosummary.

Efeito principal
----------------

- remove erro de build por falta de ``pandas`` no CI;
- estabiliza publicacao do GitHub Pages para a estrutura API/source.

Arquivo de interesse
--------------------

- ``docs/sphinx/source/conf.py``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0010-correcao-autosummary-dependencias-ci>`
