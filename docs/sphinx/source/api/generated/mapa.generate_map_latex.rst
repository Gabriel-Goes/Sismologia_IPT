mapa.generate_map_latex
=======================

.. currentmodule:: mapa

.. autofunction:: generate_map_latex

Resumo
------

Gera o bloco LaTeX do mapa principal do relatorio, incluindo legenda,
formatacao de frame e referencia ao arquivo de imagem do mapa.

Parametros
----------

- ``base_path``: diretorio base do projeto para resolver caminhos absolutos.
- ``output_filename``: arquivo ``.tex`` de saida a ser escrito.

Retorno
-------

Nao retorna valor.

Efeitos colaterais
------------------

- Escreve ``mapa.tex`` em
  ``fonte/relatorio-sismologia/tex/relatorio_preditivo/tex/``.
