# Tasks: 04-inferencia-cnn-paralela

## T1 - Implementar inferencia por evento
- Status: completed
- Verification:
  - entrada: `event.json + waveforms/*.mseed` (split ou triplet)
  - saida: bloco `rnc_prediction` no `event.json`

## T2 - Implementar runner paralelo
- Status: completed
- Verification:
  - executa lote com workers configuraveis

## T3 - Tratamento de falhas por evento
- Status: completed
- Verification:
  - erro de um evento nao interrompe lote inteiro

## T4 - Atualizar status no metadata
- Status: completed
- Verification:
  - `rnc_prediction` persistido para eventos concluidos
