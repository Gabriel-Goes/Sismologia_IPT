# Tasks: 03-base-local-eventos

## T1 - Carregar lista de eventos selecionados
- Status: pending
- Verification:
  - percorre eventos selecionados com IDs unicos

## T2 - Baixar waveform 60s por evento
- Status: pending
- Verification:
  - salva `waveform.mseed` por evento valido

## T3 - Persistir picks por estacao em event.json
- Status: pending
- Verification:
  - bloco `picks` populado quando dados existirem

## T4 - Estrategia incremental
- Status: pending
- Verification:
  - reexecucao parcial funciona sem duplicacao

## T5 - Registrar campos para SNR
- Status: pending
- Verification:
  - campo `snr` presente no schema mesmo quando null
