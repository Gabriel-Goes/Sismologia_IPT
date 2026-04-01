# Integrations

## FDSN / seisArc

- integracao principal do pipeline
- usada em Step02 para eventos/estacoes e em Step03 para waveforms
- implementada com `obspy.clients.fdsn.Client`
- configurada por `--client-url` ou por autodeteccao de host em wrappers

## Endpoint UnB

- usado apenas como health check complementar no wrapper `scripts/run_all_sisbra_build.sh`
- nao participa diretamente do caminho principal de materializacao dos bundles

## MG polygon source

- filtro geografico depende de um GeoPackage local quando disponivel
- fallback para `geobr` quando o GeoPackage nao existe ou falha
- a integracao geoespacial e parte do gate de negocio, nao um enriquecimento opcional

## Filesystem Contracts

- o pipeline inteiro depende de layout de diretorios e arquivos locais
- contratos mais importantes:
  - `event.json`
  - `event.xml`
  - `.mseed` em `waveforms/`
  - CSVs de resumo em `outputs/`

## RNC model

- modelo principal versionado em `models/rnc/model_2021354T1554.h5`
- inferencia acionada por `scripts/run_rnc_eventos_compativeis.py`
- resultado persistido em `event.json` sob `rnc_prediction`

## Legacy Compatibility Layer

- `src/seismic_event_discriminator/rnc_adapter.py` aceita:
  - naming legado dotted por canal
  - naming novo simple consolidado
- isso e uma integracao interna importante entre a base atual e artefatos historicos

## Documentation Toolchain

- fonte da documentacao em `docs/sphinx/source/`
- dependencias em `docs/sphinx/requirements.txt`
- `docs/site/` e o build publicado gerado

## Historical Baselines

- `third_party/rnc_legacy/` integra codigo legado da RNC como referencia local
- `docs/legacy_snapshot/` preserva contexto historico e decisoes passadas
- ambos devem ser lidos como referencia, nao como contrato operacional atual
