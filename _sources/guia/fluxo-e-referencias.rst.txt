Fluxo E Referencias
===================

Esta pagina segue a logica:

- User Guide -> API (objetos Python)
- API -> [source] (codigo-fonte em ``_modules``)
- Source -> [docs] (retorno para a pagina de API)

Aquisicao e normalizacao de eventos
-----------------------------------

A etapa de aquisicao usa:

- script: :doc:`fluxo_eventos.py </artefatos/fluxo-eventos-py>`;
- funcao principal: :doc:`nucleo.fluxo_eventos.fluxo_eventos </api/generated/nucleo.fluxo_eventos.fluxo_eventos>`;
- iteracao de picks: :doc:`nucleo.fluxo_eventos.iterar_eventos </api/generated/nucleo.fluxo_eventos.iterar_eventos>`;
- utilitarios: :doc:`nucleo.utils.csv2list </api/generated/nucleo.utils.csv2list>`
  e :doc:`nucleo.utils.DualOutput </api/generated/nucleo.utils.DualOutput>`.

Classificacao (RNC)
-------------------

A classificacao na RNC usa:

- script: :doc:`rnc/run.py </artefatos/rnc-run-py>`;
- entrada do fluxo: :doc:`rnc.run.main </api/generated/rnc.run.main>`;
- extracao de espectros: :doc:`rnc.data_process.spectro_extract </api/generated/rnc.data_process.spectro_extract>`;
- FFT: :doc:`rnc.data_process.get_fft </api/generated/rnc.data_process.get_fft>`;
- inferencia: :doc:`rnc.prediction.discrim </api/generated/rnc.prediction.discrim>`.

Pos-processamento e mapas
-------------------------

As etapas finais usam:

- pos-processamento (script): :doc:`pos_processa.py </artefatos/pos-processa-py>`;
- limpeza/consolidacao: :doc:`analise_dados.pos_processa.clean_data </api/generated/analise_dados.pos_processa.clean_data>`;
- consolidacao por evento: :doc:`analise_dados.pos_processa.recall_event </api/generated/analise_dados.pos_processa.recall_event>`;
- mapas (script): :doc:`gera_mapas.py </artefatos/gera-mapas-py>`;
- mapa de predicoes: :doc:`analise_dados.gera_mapas.plot_pred_map </api/generated/analise_dados.gera_mapas.plot_pred_map>`;
- macro-regioes: :doc:`analise_dados.gera_mapas.plot_macroregions </api/generated/analise_dados.gera_mapas.plot_macroregions>`.

Artefatos nao-Python
--------------------

Para scripts Bash e arquivos ``.txt``, use as paginas em :doc:`/artefatos/index`.
Nelas, o conteudo e renderizado no site e cada pagina aponta para o arquivo
fonte no GitHub.

Proximo Passo
-------------

- :doc:`API Reference </api/index>`
- :doc:`Artefatos </artefatos/index>`
