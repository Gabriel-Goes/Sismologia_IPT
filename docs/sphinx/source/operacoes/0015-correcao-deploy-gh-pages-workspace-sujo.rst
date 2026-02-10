Operacao 0015 - Correcao do deploy gh-pages para workspace sujo
================================================================

Resumo
------

Correcao do workflow de publicacao para evitar falha quando o build altera
arquivos rastreados antes do checkout de ``gh-pages``.

Efeito principal
----------------

- limpeza do workspace antes do ``git switch`` para ``gh-pages``;
- eliminacao do erro de checkout por mudancas locais.

Arquivos de interesse
---------------------

- ``.github/workflows/docs.yml``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0015-correcao-deploy-gh-pages-workspace-sujo>`

