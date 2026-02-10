rnc.run.main
============

Resumo
------

Executa o fluxo principal da RNC legado:

1. le eventos de ``arquivos/eventos/eventos.csv``;
2. extrai espectrogramas com ``spectro_extract``;
3. separa erros e dados limpos;
4. roda inferencia com ``discrim``.

Parametros
----------

- ``args``: ``argparse.Namespace`` retornado por ``read_args``.

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Salva ``arquivos/resultados/erros.csv``.
- Salva ``arquivos/resultados/pre_processado.csv``.
- Aciona escrita de ``predito.csv`` via ``discrim``.

.. currentmodule:: rnc.run

.. autofunction:: main
