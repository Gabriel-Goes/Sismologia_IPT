rnc.run.read\_args
==================

Resumo
------

Define e parseia argumentos de linha de comando do pipeline legado da RNC.

Parametros
----------

Nao recebe parametros diretamente; le ``sys.argv``.

Retorno
-------

Retorna ``argparse.Namespace`` com:

- ``model``
- ``mseed_dir``
- ``spectro_dir``
- ``output_dir``
- ``valid``

Observacao
----------

A flag ``--valid`` e declarada, mas nao e usada no fluxo principal atual.

.. currentmodule:: rnc.run

.. autofunction:: read_args
