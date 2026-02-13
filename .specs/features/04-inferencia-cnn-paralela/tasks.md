# Tasks: 04-inferencia-cnn-paralela

## T1 - Implementar inferencia por evento
- Status: pending
- Verification:
  - entrada: `event.json + waveform.mseed`
  - saida: `prediction.json`

## T2 - Implementar runner paralelo
- Status: pending
- Verification:
  - executa lote com workers configuraveis

## T3 - Tratamento de falhas por evento
- Status: pending
- Verification:
  - erro de um evento nao interrompe lote inteiro

## T4 - Atualizar status no metadata
- Status: pending
- Verification:
  - `cnn_processed=true` para eventos concluidos
