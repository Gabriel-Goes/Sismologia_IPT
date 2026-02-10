rnc.data\_process.spectro\_extract
==================================

Resumo
------

Pre-processa picks de ``.mseed`` para gerar espectrogramas ``.npy`` e metadados
auxiliares (CFT, warnings e erros) para a etapa de classificacao da RNC.

Parametros
----------

- ``mseed_dir``: diretorio de entrada (parametro legado; o caminho efetivo de
  leitura usa ``arquivos/mseed/{Path}``).
- ``spectro_dir``: diretorio de saida dos espectrogramas.
- ``eventos``: ``pandas.DataFrame`` com colunas como ``Event``, ``Station`` e
  ``Path``.

Retorno
-------

Retorna ``eventos`` com colunas adicionais, incluindo ``Compo``, ``CFT``,
``Error`` e ``Warning``.

Efeitos colaterais
------------------

- Salva arquivos ``.npy`` em ``{spectro_dir}/{Event}/``.
- Registra erros de consistencia (componentes, shape esperado, arquivo ausente).

Observacao
----------

A funcao espera shape de espectrograma ``(237, 50)`` por componente e exige 3
componentes para salvar o evento.

.. currentmodule:: rnc.data_process

.. autofunction:: spectro_extract
