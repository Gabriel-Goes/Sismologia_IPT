# Operacao 0013 - Fluxo legado do fluxo_sismo.sh em Visao Geral

**Data:** 2026-02-10  
**Branch:** `docs/api-topo-preview`  
**Contexto:** `legado`

## Objetivo

Comecar a documentacao funcional da codebase legado a partir do orquestrador
principal `fluxo_sismo.sh`, descrevendo o que ele executa de ponta a ponta.

## Escopo executado

1. Leitura linha a linha de:
   - `.specs/codebase/fluxo_sismo.sh`

2. Consolidacao no `Visao Geral` de:
   - entrada e flags do pipeline;
   - ordem de execucao por etapa;
   - scripts Python chamados em cada etapa;
   - artefatos principais gerados;
   - dependencias-chave por dominio.

Arquivo alterado:

- `docs/sphinx/source/visao_geral.rst`

## Resultado

`Visao Geral` agora explicita como o legado opera de fato:

- tratamento de catalogo (`pre_processa.py`);
- aquisicao (`fluxo_eventos.py`);
- inferencia (`rnc/run.py`);
- pos-processamento (`pos_processa.py`);
- mapas (`gera_mapas.py`);
- relatorio (`figures.py`, `mapa.py`, `pdflatex`).

## Proximo passo natural

Detalhar os contratos de entrada/saida de cada etapa (colunas CSV e caminhos)
em pagina dedicada do trilho legado, mantendo o `Visao Geral` como mapa macro.
