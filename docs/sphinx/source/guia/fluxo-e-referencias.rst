Fluxo E Referencias
===================

Esta pagina segue a logica:

- User Guide -> API (objetos Python)
- API -> [source] (codigo-fonte em ``_modules``)
- Source -> [docs] (retorno para a pagina de API)

Aquisicao e normalizacao de eventos
-----------------------------------

O fluxo de entrada usa:

- pre-processamento (source):
  `analise_dados/pre_processa.py <../_modules/analise_dados/pre_processa.html#main>`_;
- entrypoint: :doc:`analise_dados.pre_processa.main </api/generated/analise_dados.pre_processa.main>`.

Depois, a aquisicao usa:

- script (source): `nucleo/fluxo_eventos.py <../_modules/nucleo/fluxo_eventos.html#fluxo_eventos>`_;
- funcao principal: :doc:`nucleo.fluxo_eventos.fluxo_eventos </api/generated/nucleo.fluxo_eventos.fluxo_eventos>`;
- iteracao de picks: :doc:`nucleo.fluxo_eventos.iterar_eventos </api/generated/nucleo.fluxo_eventos.iterar_eventos>`;
- utilitarios: :doc:`nucleo.utils.csv2list </api/generated/nucleo.utils.csv2list>`
  e :doc:`nucleo.utils.DualOutput </api/generated/nucleo.utils.DualOutput>`.

Classificacao (RNC)
-------------------

A classificacao na RNC usa:

- script (source): `rnc/run.py <../_modules/rnc/run.html#main>`_;
- entrada do fluxo: :doc:`rnc.run.main </api/generated/rnc.run.main>`;
- extracao de espectros: :doc:`rnc.data_process.spectro_extract </api/generated/rnc.data_process.spectro_extract>`;
- FFT: :doc:`rnc.data_process.get_fft </api/generated/rnc.data_process.get_fft>`;
- inferencia: :doc:`rnc.prediction.discrim </api/generated/rnc.prediction.discrim>`.

Pos-processamento e mapas
-------------------------

As etapas finais usam:

- pos-processamento (source):
  `analise_dados/pos_processa.py <../_modules/analise_dados/pos_processa.html#main>`_;
- limpeza/consolidacao: :doc:`analise_dados.pos_processa.clean_data </api/generated/analise_dados.pos_processa.clean_data>`;
- consolidacao por evento: :doc:`analise_dados.pos_processa.recall_event </api/generated/analise_dados.pos_processa.recall_event>`;
- mapas (source):
  `analise_dados/gera_mapas.py <../_modules/analise_dados/gera_mapas.html#main>`_;
- entrypoint de mapas: :doc:`analise_dados.gera_mapas.main </api/generated/analise_dados.gera_mapas.main>`;
- mapa de predicoes: :doc:`analise_dados.gera_mapas.plot_pred_map </api/generated/analise_dados.gera_mapas.plot_pred_map>`;
- macro-regioes: :doc:`analise_dados.gera_mapas.plot_macroregions </api/generated/analise_dados.gera_mapas.plot_macroregions>`.

Relatorio
---------

Para fechamento do pipeline:

- script (source): `figures.py <../_modules/figures.html#generate_latex_for_figures>`_;
- docs: :doc:`figures.generate_latex_for_figures </api/generated/figures.generate_latex_for_figures>`;
- script (source): `mapa.py <../_modules/mapa.html#generate_map_latex>`_;
- docs: :doc:`mapa.generate_map_latex </api/generated/mapa.generate_map_latex>`.

Artefatos nao-Python
--------------------

Para scripts Bash e arquivos ``.txt``, use as paginas em :doc:`/artefatos/index`.
Nelas, o conteudo e renderizado no site e cada pagina aponta para o arquivo
fonte no GitHub.

Proximo Passo
-------------

- :doc:`API Reference </api/index>`
- :doc:`Artefatos </artefatos/index>`
