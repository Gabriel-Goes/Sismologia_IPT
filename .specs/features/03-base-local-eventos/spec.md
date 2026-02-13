# Feature Spec: 03-base-local-eventos

## Problem
Sem base local por evento, fica dificil ampliar o estudo no futuro sem
reprocessar tudo e sem rastrear a evolucao dos dados.

## Goal
Construir base local de analise por evento, acoplando metadados e waveform.

## Inputs
- Arquivos por evento da feature 01 (`event.json` e opcional `event.xml`).
- Endpoint FDSN para aquisicao de waveform.

## Outputs
- `data/events/<event_id>/waveform.mseed`
- `event.json` atualizado com picks e status.

## Requirements
1. Download de waveform em janela de 60s.
2. Persistir picks por estacao quando disponiveis.
3. Base incremental (nao recriar tudo em cada run).
4. Preparar campos para SNR por pick (mesmo que calculo venha depois).

## Acceptance Criteria
1. Lote de teste cria par `event.json + waveform.mseed` para eventos validos.
2. Reexecucao nao duplica eventos processados.
3. Campos de status permitem retomar processamento parcial.
