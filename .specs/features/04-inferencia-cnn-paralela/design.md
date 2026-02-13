# Design: 04-inferencia-cnn-paralela

## Strategy
1. Script python processa um evento por chamada.
2. Runner paralelo despacha N eventos em workers.
3. Cada worker grava resultado no diretorio do proprio evento.

## Parallel Options
- Shell com runner paralelo (estilo runp.sh).
- Python com `concurrent.futures.ProcessPoolExecutor`.

## Chosen Start
Comecar com shell runner simples para menor atrito operacional.

## Output Contract
`prediction.json` (preferencial v1):
```json
{
  "event_id": "uspXXXX",
  "model": "cnn_v1",
  "pick_predictions": [],
  "event_score_natural": 0.73,
  "event_label": "natural"
}
```

Em seguida, espelhar resumo em `event.json.status`.
