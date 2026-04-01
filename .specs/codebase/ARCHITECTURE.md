# Architecture

**Pattern:** pipeline modular orientado a arquivos, com CLIs Python e wrappers Bash.

## High-Level Structure

```text
SISBRA RAW/CSV
  -> normalize_sisbra_raw.py
  -> filter_sisbra_csv.py
  -> step01_catalogo_selecao.py / step02_fdsn_picks_export.py
  -> step03_waveforms_from_p_picks.py
  -> organize_compatible_events.py
  -> enforce_triplet_channels.py
  -> run_rnc_eventos_compativeis.py
```

## Main Runtime Flow

### 1. Catalog preparation

- `scripts/normalize_sisbra_raw.py` transforma o RAW SISBRA em CSV derivado do projeto.
- `scripts/filter_sisbra_csv.py` aplica gate geografico e filtros de negocio antes do FDSN.
- `src/seismic_event_discriminator/step01_catalogo_selecao.py` concentra parsing do CSV SISBRA e matching com catalogo FDSN estatico quando necessario.

### 2. Step02 bundle export

- `src/seismic_event_discriminator/step02_fdsn_picks_export.py` consulta FDSN live, escolhe o melhor candidato por tempo/distancia/magnitude e exporta um bundle por evento.
- O bundle persistido em disco e o contrato central do pipeline:
  - `event.xml`: QuakeML do evento selecionado
  - `event.json`: dados SISBRA, match FDSN, picks filtrados e `waveform_download_contract`
- Eventos `matched`, `ambiguous` e `no_match` podem ser materializados em roots diferentes.

### 3. Step03 waveform acquisition

- `scripts/step03_waveforms_from_p_picks.py` le `event.json`, seleciona picks `P*`, baixa janelas de waveform e escreve MiniSEED.
- O script suporta dois formatos de saida:
  - legado por componente: `NET.STA.LOC.CHA_PICKTIME.mseed`
  - formato consolidado atual: `NET_STA_DATETIME.mseed`
- O contrato vindo do Step02 define padrao de nome e canais quando a CLI nao sobrescreve isso.

### 4. Compatibility gates

- `scripts/organize_compatible_events.py` decide se um evento vai para `eventos_compativeis` ou `eventos_nao_compativeis`.
- Os gates combinam:
  - `match_status`
  - ponto-no-poligono MG
  - magnitude/profundidade
  - existencia de pick `P*`
  - existencia de waveform baixada
  - opcionalmente `min-year`
- `scripts/enforce_triplet_channels.py` faz um gate adicional exigindo triplet 3C valido.

### 5. RNC inference

- `scripts/run_rnc_eventos_compativeis.py` descobre triplets em cada evento compativel e executa a inferencia Natural vs Anthropogenic.
- `src/seismic_event_discriminator/rnc_adapter.py` faz a ponte entre os nomes/arquivos do projeto e o input esperado pela inferencia.
- O resultado e persistido de volta no `event.json` e em tres CSVs de auditoria.

## Architectural Patterns Observed

### Filesystem as system of record

- O estado do pipeline nao fica em banco; fica em pastas, JSONs, XMLs, CSVs e arquivos `.mseed`.
- Cada etapa assume o layout produzido pela etapa anterior.

### Script-first orchestration

- A logica reutilizavel esta em `src/`, mas a operacao real acontece por CLIs em `scripts/`.
- Wrappers Bash registram ambiente, health checks, logs e resumos de lote.

### Defensive parsing over strict typing

- O codigo usa muitos helpers `_safe_*`, normalizacao de strings e `try/except` para lidar com dados heterogeneos.
- Isso aumenta robustez operacional, mas os contratos ficam implícitos e pouco formalizados.

### Backward compatibility in waveform naming

- O adapter e os gates precisam aceitar simultaneamente naming legado e naming novo.
- Isso reduz ruptura em bases antigas, mas aumenta o risco de drift entre scripts e artefatos.

## Module Boundaries

- `src/seismic_event_discriminator/`
  - parsing SISBRA/FDSN
  - filtro geografico
  - adapter e inferencia RNC
- `scripts/`
  - orquestracao operacional
  - preprocessamento
  - download
  - gates
  - runners de lote
- `third_party/rnc_legacy/`
  - referencia historica da RNC original
- `docs/legacy_snapshot/`
  - snapshot documental historico, fora do baseline vivo

## Data Contracts That Matter

- `event.json` e o contrato central entre Step02, Step03, gates e RNC.
- O summary CSV do Step03 participa do gate de compatibilidade.
- O layout/nome dos `.mseed` participa do gate de triplet e da descoberta de inputs da RNC.

## Operational Boundaries

- O pipeline depende fortemente de ambiente local, rede e filesystem.
- `docs/` contem runbooks e memoria operacional; `.specs/` e a camada canônica para mapeamento e planejamento.
