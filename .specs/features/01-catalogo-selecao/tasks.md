# Tasks: 01-catalogo-selecao

## T1 - Implementar leitura do catalogo SISBRA e normalizacao minima
- Status: completed
- Verification:
  - leitura de `catalogo_RAW_v2024May09.csv` operacional
  - etapa propria de normalizacao gera CSV derivado + auditoria de coordenadas invalidas

## T2 - Implementar filtro unico (etapas 1+2) com regras explicitas
- Status: completed
- Verification:
  - filtros lineares operacionais: geometria MG (ponto-poligono) -> magnitude -> profundidade -> ano (ultimo gate)
  - `ST` mantido apenas para auditoria (`st_geo_consistency`), sem uso como gate de inclusao
  - total selecionado registrado

## T3 - Quebrar eventos em arquivos por evento
- Status: completed
- Verification:
  - gera `event.json` por evento
  - gera `event.xml` quando houver match FDSN

## T4 - Notebook de selecao
- Status: completed
- Verification:
  - notebook executa do inicio ao fim
  - output legivel para orientadores
