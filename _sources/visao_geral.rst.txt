Visao Geral
===========

Objetivo
--------

Reescrever o fluxo do projeto de classificacao sismologica com arquitetura mais
limpa, modular e auditavel, mantendo rastreabilidade tecnica para avaliacao
academica.

Estrutura de trabalho
---------------------

- ``.specs/codebase/``: baseline legado (fonte de consulta).
- ``.specs/project/``: planejamento e memoria de execucao.
- ``docs/operacoes/``: diario de operacoes por commit.
- ``docs/sphinx/``: publicacao da documentacao via GitHub Pages.
- ``docs/sphinx/source/guia/``: user guide com links para API.
- ``docs/sphinx/source/api/``: referencia de funcoes e classes.
- ``docs/sphinx/source/artefatos/``: scripts e arquivos txt renderizados.

Diretriz de execucao
--------------------

Cada operacao relevante deve:

1. gerar alteracoes pequenas e verificaveis;
2. ser registrada em arquivo de operacao;
3. ser commitada isoladamente.

Publicacao
----------

A documentacao HTML e gerada com Sphinx e publicada no GitHub Pages por
workflow automatizado.

Continue A Leitura
------------------

Proximo passo recomendado:

- :doc:`User Guide </guia/index>`

Atalhos:

- :doc:`API Reference </api/index>`
- :doc:`Operacoes </operacoes/index>`
