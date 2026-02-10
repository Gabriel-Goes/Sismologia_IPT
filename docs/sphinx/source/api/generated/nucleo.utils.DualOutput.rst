nucleo.utils.DualOutput
=======================

.. currentmodule:: nucleo.utils

.. autoclass:: DualOutput
   :members: __init__, write, flush

Resumo
------

Classe utilitaria para duplicar escrita de saida em dois destinos:

- terminal (stdout atual);
- arquivo de log em modo append.

Uso tipico
----------

Substituir ``sys.stdout`` por uma instancia de ``DualOutput`` para gravar logs
sem perder a visualizacao no terminal.

