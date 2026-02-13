# Design: 01-catalogo-selecao

## Processing Flow
1. Ler catalogo bruto da origem (QuakeML ou builder text).
2. Normalizar estrutura em tabela temporaria para filtro.
3. Aplicar filtros espaciais e fisicos.
4. Para cada evento selecionado:
   - criar pasta `data/events/<event_id>/`,
   - escrever `event.json`,
   - escrever `event.xml` quando disponivel.

## Why This Design
- Mantem simplicidade de leitura no notebook.
- Preserva padrao sismologico via QuakeML.
- Garante flexibilidade com JSON para extensoes futuras.

## Minimal event.json (v1)
```json
{
  "event_id": "uspXXXX",
  "origin_time": "2026-01-01T00:00:00Z",
  "latitude": -20.0,
  "longitude": -44.0,
  "depth_km": 5.0,
  "magnitude": 2.5,
  "picks": [],
  "status": {
    "selected": true,
    "waveform_downloaded": false,
    "cnn_processed": false
  }
}
```

## Implementation Style
- Notebook de selecao primeiro.
- Script python equivalente em paralelo para execucao linear.
