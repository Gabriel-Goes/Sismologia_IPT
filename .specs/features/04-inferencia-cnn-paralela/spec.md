# Feature Spec: 04-inferencia-cnn-paralela

## Problem
Inferencia evento-a-evento em sequencia fica lenta e nao escala para lotes
maiores.

## Goal
Executar inferencia da CNN por evento com suporte a processamento paralelo.

## Inputs
- `event.json` por evento compativel
- arquivos `.mseed` por evento (split por canal ou triplet por estacao)

## Outputs
- atualizar `event.json` com bloco `rnc_prediction`
- gerar CSVs de auditoria (`events`, `picks`, `errors`)

## Requirements
1. Unidade de trabalho independente por evento.
2. Suporte a N workers configuravel.
3. Falhas por evento nao devem abortar lote inteiro.
4. Resultado deve ser rastreavel por evento.
5. Persistencia da inferencia deve ocorrer no proprio `event.json`.

## Acceptance Criteria
1. Lote de teste executa com workers > 1.
2. Eventos processados ficam marcados no metadata.
3. Saida da CNN fica persistida por evento.
