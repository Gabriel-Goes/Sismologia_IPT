Operacao 0017 - Runner de matriz de testes e guia operacional
==============================================================

Resumo
------

Consolidacao de um runner dedicado para matriz de testes com arquivamento de
artefatos e documentacao operacional no User Guide.

Efeito principal
----------------

- execucao padronizada da matriz com arquivamento no repositorio;
- isolamento entre execucoes para evitar copia de logs antigos;
- trilha de navegacao do User Guide atualizada com pagina de testes;
- memoria de ambiente `pyenv` registrada para reproducao local.

Arquivos de interesse
---------------------

- ``scripts/dev/run_fluxo_test_matrix_archived.sh``
- ``docs/sphinx/source/guia/execucoes-de-teste-fluxo-legado.rst``
- ``docs/sphinx/source/guia/index.rst``
- ``docs/sphinx/source/guia/fluxo-e-referencias.rst``
- ``documentação/memoria_ambiente_pyenv_virtualenv.md``
- ``documentação/README.md``
- ``.python-version``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0017-runner-matriz-testes-e-guia-operacional>`
