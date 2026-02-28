# Tasks: 03-base-local-eventos

## T1 - Carregar lista de eventos selecionados
- Status: completed
- Verification:
  - percorre eventos selecionados com IDs unicos

## T2 - Baixar waveform 60s por evento
- Status: completed
- Verification:
  - salva waveform por estacao/canal ou triplet por estacao
  - janela `P-10s` a `P+50s` aplicada

## T3 - Persistir picks por estacao em event.json
- Status: completed
- Verification:
  - bloco `picks` populado quando dados existirem

## T4 - Estrategia incremental
- Status: completed
- Verification:
  - reexecucao parcial funciona sem duplicacao

## T5 - Registrar campos para SNR
- Status: pending
- Verification:
  - campo `snr` presente no schema mesmo quando null
