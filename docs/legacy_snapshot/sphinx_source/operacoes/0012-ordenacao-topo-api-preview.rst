Operacao 0012 - Ordenacao de metodos no topo da API (preview)
==============================================================

Resumo
------

Ajuste de apresentacao das paginas de API para mostrar assinatura/metodo no
topo, mantendo as descricoes detalhadas adicionadas na operacao 0011.

Efeito principal
----------------

- melhora escaneabilidade tecnica da pagina;
- preserva texto explicativo logo abaixo da assinatura;
- usa modo hibrido de autosummary (gera faltantes sem sobrescrever manuais).
- inclui skill para decidir consolidacao vs nova operacao no diario.
- adiciona fluxo de navegacao continuo entre as secoes principais do site.
- formaliza separacao entre objetivo da refatoracao e objetivo do legado.

Arquivos de interesse
---------------------

- ``docs/sphinx/source/api/generated/*.rst``
- ``docs/sphinx/source/conf.py``
- ``skills/operation-journal-consolidator/``
- ``docs/sphinx/source/index.rst``
- ``docs/sphinx/source/visao_geral.rst``
- ``docs/sphinx/source/guia/``
- ``docs/sphinx/source/api/index.rst``
- ``docs/sphinx/source/artefatos/index.rst``
- ``docs/sphinx/source/operacoes/index.rst``
- ``docs/sphinx/source/dois_objetivos.rst``
- ``.specs/project/PROJECT.md``
- ``.specs/project/ROADMAP.md``
- ``.specs/project/STATE.md``
- ``documentação/README.md``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0012-ordenacao-topo-api-preview>`
- :doc:`API Reference </api/index>`
