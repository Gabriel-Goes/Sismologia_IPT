Visao Geral
===========

Esta branch inicia uma nova historia do projeto, sem dependencia do historico de
commits anteriores, para permitir reescrita completa com foco em qualidade de
engenharia e rastreabilidade academica.

Fluxo alvo (v3)
---------------

1. Construcao de catalogo a partir de consulta MOHO.
2. Selecao de eventos em regiao de atividade mineira em MG (``M < 4.9`` e ``depth < 10 km``).
3. Aquisicao de formas de onda (janela de 60 s).
4. Preparacao de entrada da CNN (``.mseed -> .npy``).
5. Analise dos resultados (graficos e mapas).

Implementacao atual
-------------------

- Etapas 1+2 comecadas em ``src/seismic_event_discriminator/step01_catalogo_selecao.py``.
- Notebooks didaticos no diretorio ``notebooks/`` para execucao e validacao no SEISAPP.
