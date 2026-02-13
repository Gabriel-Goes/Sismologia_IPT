# Feature Spec: 05-analise-resultados

## Problem
Sem consolidacao analitica, os resultados da inferencia ficam dificeis de
interpretar e comunicar.

## Goal
Gerar notebooks de analise com tabelas, graficos e mapas para leitura academica.

## Inputs
- `event.json` e `prediction.json` por evento.
- Dados derivados das etapas anteriores.

## Outputs
- Notebooks executaveis com graficos e mapas.
- Tabelas finais de apoio (csv/parquet).
- Figuras principais para relatorio.

## Requirements
1. Analise por evento e agregada por conjunto.
2. Indicadores minimos:
   - contagem por classe,
   - distribuicao espacial,
   - metricas de confianca.
3. Notebook legivel por orientador sem abrir codigo interno.

## Acceptance Criteria
1. Notebook abre e executa fim-a-fim com dataset de teste.
2. Graficos e mapas ficam salvos em `outputs/`.
3. Resultados podem ser revisados sem depender de scripts auxiliares.
