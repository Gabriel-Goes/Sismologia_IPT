rnc.prediction.discrim
======================

Resumo
------

Executa inferencia da rede convolucional nos espectrogramas por pick, agrega
probabilidades por evento e grava o resultado final em CSV.

Parametros
----------

- ``model``: caminho para arquivo ``.h5`` do modelo treinado.
- ``spectro_dir``: diretorio com espectrogramas por evento.
- ``output_dir``: diretorio onde salvar ``predito.csv``.
- ``eventos``: ``pandas.DataFrame`` com metadados de pick/evento.

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Atualiza colunas de predicao por pick e por evento no ``DataFrame``.
- Salva ``{output_dir}/predito.csv``.

.. currentmodule:: rnc.prediction

.. autofunction:: discrim
