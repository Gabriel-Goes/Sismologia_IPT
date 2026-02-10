API Reference
=============

Referencia de funcoes e classes usadas no fluxo legado. Cada objeto abaixo
aponta para pagina dedicada com explicacao de comportamento, assinatura,
docstring e botao ``[source]``.

Escopo atual: modulos que permitem import seguro no build de documentacao.
Scripts com parse de argumentos em tempo de importacao permanecem em
:doc:`/artefatos/index` ate serem refatorados.

Fluxo De Navegacao
------------------

- Voltar para contexto de leitura: :doc:`/guia/index`
- Seguir para scripts e arquivos texto: :doc:`/artefatos/index`
- Consultar historico de mudancas: :doc:`/operacoes/index`

Entrypoints Do Fluxo Legado
---------------------------

.. autosummary::
   :toctree: generated/

   analise_dados.pre_processa.main
   nucleo.fluxo_eventos.fluxo_eventos
   rnc.run.main
   analise_dados.pos_processa.main
   analise_dados.gera_mapas.main
   figures.generate_latex_for_figures
   mapa.generate_map_latex

Nucleo
------

.. autosummary::
   :toctree: generated/

   nucleo.fluxo_eventos.iterar_eventos
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

Analise De Dados
----------------

.. autosummary::
   :toctree: generated/

   analise_dados.gera_mapas.plot_pred_map
   analise_dados.gera_mapas.plot_macroregions
   analise_dados.pos_processa.clean_data
   analise_dados.pos_processa.recall_event
