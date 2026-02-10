API Reference
=============

Referencia de funcoes e classes usadas no fluxo legado. Cada objeto abaixo
aponta para pagina dedicada com explicacao de comportamento, assinatura,
docstring e botao ``[source]``.

Escopo atual: modulos que permitem import seguro no build de documentacao.
Scripts com parse de argumentos em tempo de importacao permanecem em
:doc:`/artefatos/index` ate serem refatorados.

Nucleo
------

.. autosummary::
   :toctree: generated/

   nucleo.fluxo_eventos.iterar_eventos
   nucleo.fluxo_eventos.fluxo_eventos
   nucleo.fluxo_eventos.main
   nucleo.utils.DualOutput
   nucleo.utils.csv2list

RNC
---

.. autosummary::
   :toctree: generated/

   rnc.data_process.get_fft
   rnc.data_process.spectro_extract
   rnc.prediction.discrim
   rnc.run.read_args
   rnc.run.main

Analise De Dados
----------------

.. autosummary::
   :toctree: generated/

   analise_dados.gera_mapas.plot_pred_map
   analise_dados.gera_mapas.plot_macroregions
   analise_dados.pos_processa.clean_data
   analise_dados.pos_processa.recall_event
