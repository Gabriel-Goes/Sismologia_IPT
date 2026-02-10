analise\_dados.pos\_processa.recall\_event
==========================================

.. currentmodule:: analise_dados.pos_processa

.. autofunction:: recall_event

Resumo
------

Calcula e plota a variacao do recall por evento conforme um limiar minimo de
``SNR_P``, com filtros de distancia e magnitude.

Parametros
----------

- ``df``: ``pandas.DataFrame`` com colunas como ``Distance``, ``MLv``,
  ``SNR_P``, ``Event Prob_Nat`` e ``Label``.
- ``d``: limite maximo de distancia (km). Padrao: ``400``.
- ``m``: limite maximo de magnitude. Padrao: ``8``.

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Gera grafico de recall em ``arquivos/figuras/pos_processa/{d}{m}_recall_event.png``.

Observacao
----------

O filtro por ``SNR_P`` e aplicado de forma acumulativa dentro do loop de limiar,
o que reduz progressivamente o conjunto usado nas iteracoes seguintes.

