# Tasks: 01-catalogo-selecao

## T1 - Implementar leitura do catalogo SISBRA e normalizacao minima
- Status: completed
- Verification:
  - leitura de `catalogo_CLEAN_v2024May09.csv` operacional
  - contagem de entrada registrada no filtro

## T2 - Implementar filtro unico (etapas 1+2) com regras explicitas
- Status: completed
- Verification:
  - filtros lineares operacionais: estado -> ano -> magnitude -> profundidade
  - total selecionado registrado

## T3 - Quebrar eventos em arquivos por evento
- Status: completed
- Verification:
  - gera `event.json` por evento
  - gera `event.xml` quando houver match FDSN

## T4 - Notebook de selecao
- Status: pending
- Verification:
  - notebook executa do inicio ao fim
  - output legivel para orientadores
