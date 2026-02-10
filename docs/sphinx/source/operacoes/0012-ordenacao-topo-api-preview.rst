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

Arquivos de interesse
---------------------

- ``docs/sphinx/source/api/generated/*.rst``
- ``docs/sphinx/source/conf.py``
- ``skills/operation-journal-consolidator/``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0012-ordenacao-topo-api-preview>`
- :doc:`API Reference </api/index>`
