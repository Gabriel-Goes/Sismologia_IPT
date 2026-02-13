# Design: 03-base-local-eventos

## Directory Contract
```
data/events/
  <event_id>/
    event.json
    event.xml        # opcional
    waveform.mseed
```

## update rules
1. Se `event.json` ja existe, atualizar apenas campos derivados.
2. Se `waveform.mseed` ja existe e nao houver `--force`, pular download.
3. Registrar erros por evento sem interromper lote completo.

## event.json extension (v2)
```json
{
  "picks": [
    {
      "network": "XX",
      "station": "ABCD",
      "channel": "HHZ",
      "phase": "P",
      "pick_time": "2026-01-01T00:00:10Z",
      "snr": null
    }
  ],
  "status": {
    "selected": true,
    "waveform_downloaded": true,
    "cnn_processed": false
  }
}
```

## Implementation Style
- Primeiro: notebook da etapa 3.
- Depois: script linear equivalente para reproducao batch.
