Fluxo E Referencias
===================

Esta pagina segue a logica:

- User Guide -> API (objetos Python)
- API -> [source] (codigo-fonte em ``_modules``)
- Source -> [docs] (retorno para a pagina de API)

Aquisicao e normalizacao de eventos
-----------------------------------

A etapa de aquisicao usa
`nucleo.fluxo_eventos.fluxo_eventos <../api/generated/nucleo.fluxo_eventos.fluxo_eventos.html#nucleo.fluxo_eventos.fluxo_eventos>`_,
que internamente itera picks com
`nucleo.fluxo_eventos.iterar_eventos <../api/generated/nucleo.fluxo_eventos.iterar_eventos.html#nucleo.fluxo_eventos.iterar_eventos>`_.
Rotinas auxiliares como
`nucleo.utils.csv2list <../api/generated/nucleo.utils.csv2list.html#nucleo.utils.csv2list>`_
e
`nucleo.utils.DualOutput <../api/generated/nucleo.utils.DualOutput.html#nucleo.utils.DualOutput>`_
suportam parse de catalogo e log.

Classificacao (RNC)
-------------------

A extracao de espectros e realizada por
`rnc.data_process.spectro_extract <../api/generated/rnc.data_process.spectro_extract.html#rnc.data_process.spectro_extract>`_
(com FFT em
`rnc.data_process.get_fft <../api/generated/rnc.data_process.get_fft.html#rnc.data_process.get_fft>`_)
e a inferencia por
`rnc.prediction.discrim <../api/generated/rnc.prediction.discrim.html#rnc.prediction.discrim>`_,
orquestrada por
`rnc.run.main <../api/generated/rnc.run.main.html#rnc.run.main>`_.

Pos-processamento e mapas
-------------------------

A consolidacao de metricas pode ser lida em
`analise_dados.pos_processa.clean_data <../api/generated/analise_dados.pos_processa.clean_data.html#analise_dados.pos_processa.clean_data>`_
e
`analise_dados.pos_processa.recall_event <../api/generated/analise_dados.pos_processa.recall_event.html#analise_dados.pos_processa.recall_event>`_.
A geracao de mapas e feita por
`analise_dados.gera_mapas.plot_pred_map <../api/generated/analise_dados.gera_mapas.plot_pred_map.html#analise_dados.gera_mapas.plot_pred_map>`_
e
`analise_dados.gera_mapas.plot_macroregions <../api/generated/analise_dados.gera_mapas.plot_macroregions.html#analise_dados.gera_mapas.plot_macroregions>`_.

Artefatos nao-Python
--------------------

Para scripts Bash e arquivos ``.txt``, use as paginas em :doc:`/artefatos/index`.
Nelas, o conteudo e renderizado no site e cada pagina aponta para o arquivo fonte
no GitHub.

Proximo Passo
-------------

- :doc:`API Reference </api/index>`
- :doc:`Artefatos </artefatos/index>`
