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
Bloco `rnc_prediction` persistido no `event.json`:
```json
{
  "rnc_prediction": {
    "model_path": "models/rnc/model_2021354T1554.h5",
    "status": "ok",
    "event_label": "natural",
    "event_score_natural": 0.73,
    "pick_predictions": []
  }
}
```

Resumo agregado exportado em CSVs para auditoria.
