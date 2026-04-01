# Project Structure

**Root:** `/Users/wiser/projects/gabrielgoes/Sismologia_IPT`

## Topology

```text
.
├── .specs/
│   ├── codebase/
│   ├── features/
│   └── project/
├── catalogs/
│   └── sisbra/
├── docs/
│   ├── legacy_snapshot/
│   ├── site/
│   └── sphinx/
├── models/
│   └── rnc/
├── notebooks/
├── outputs/
├── scripts/
│   ├── dev/
│   └── legacy/
├── src/
│   └── seismic_event_discriminator/
└── third_party/
    └── rnc_legacy/
```

## What Lives Where

### `src/seismic_event_discriminator/`

- nucleo Python reutilizavel do pipeline
- parsing SISBRA/FDSN
- filtro geografico de MG
- adapter e inferencia RNC

### `scripts/`

- CLIs operacionais do pipeline
- preprocessamento e filtros
- runners de lote, smoke e inferencia
- `scripts/legacy/` guarda diagnosticos historicos fora do fluxo principal

### `catalogs/`

- insumos de catalogo e query builders
- `catalogs/sisbra/` contem dados e utilitarios associados ao catalogo SISBRA

### `models/rnc/`

- artefato versionado do modelo `.h5` usado na inferencia

### `notebooks/`

- notebooks self-contained por etapa para auditoria e exploracao

### `docs/`

- `docs/legacy_snapshot/`: snapshot historico
- `docs/sphinx/`: fonte da documentacao publicada
- `docs/site/`: build gerado do site Sphinx
- `docs/*.md`: runbooks e memoria operacional

### `.specs/`

- baseline de planejamento, estado e mapeamento brownfield
- `codebase/` deve documentar o codigo atual, nao o historico

## Active Execution Path

1. `scripts/normalize_sisbra_raw.py`
2. `scripts/filter_sisbra_csv.py`
3. `src/seismic_event_discriminator/step02_fdsn_picks_export.py`
4. `scripts/step03_waveforms_from_p_picks.py`
5. `scripts/organize_compatible_events.py`
6. `scripts/enforce_triplet_channels.py`
7. `scripts/run_rnc_eventos_compativeis.py`

## Historical or Auxiliary Areas

- `third_party/rnc_legacy/` e codigo de referencia legado
- `scripts/legacy/` e utilitario de diagnostico historico
- `docs/legacy_snapshot/` e snapshot documental congelado
- `docs/site/` e artefato buildado, nao fonte primaria

## Structure Notes

- `data/` nao aparece no tree versionado porque esta ignorado, mas e central em runtime.
- `outputs/` tambem e ignorado como artefato operacional, embora exista no workspace.
- o repositório mistura codigo, dados de apoio, modelo e documentacao operacional no mesmo root.
