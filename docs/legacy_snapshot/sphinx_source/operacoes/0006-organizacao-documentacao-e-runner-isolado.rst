Operacao 0006 - Organizacao da documentacao e runner isolado
=============================================================

Resumo
------

Consolidacao da documentacao da iteracao v2 na raiz do repositorio e adicao
de um runner isolado para executar o baseline sem poluir a worktree principal
com artefatos de teste.

Efeito principal
----------------

- separacao clara entre baseline legado e documentacao da iteracao v2;
- reducao de risco de commit acidental de arquivos gerados pelo pipeline;
- registro das diretrizes iniciais para escrita do paper tecnico.

Arquivos/diretorios de interesse
--------------------------------

- ``documentação/``
- ``scripts/dev/run_fluxo_isolated.sh``
- ``documentação/Possible_Paper_OutLine.md``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0006-organizacao-documentacao-e-runner-isolado>`
- :doc:`Outline do paper </detalhes/possible-paper-outline>`
- :doc:`Conexao no User Guide (encapsulamento) </guia/scripts-de-encapsulamento>`
