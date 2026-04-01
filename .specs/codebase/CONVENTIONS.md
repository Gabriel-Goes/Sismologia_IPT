# Code Conventions

## Naming Conventions

### Python and modules

- arquivos Python em `snake_case`
- funcoes auxiliares privadas com prefixo `_`
- dataclasses para contratos pequenos (`SisbraEvent`, `FdsnEvent`, `TripletInput`)
- constantes em `UPPER_SNAKE_CASE`

### Event folders

- bundles do Step02: `YYYYMMDDTHHMMSS[_eventid]`
- pasta final de compativeis: `YYYYMMDDTHHMMSS`

### Waveform files

- legado split: `NET.STA.LOC.CHA_PICKTIME.mseed`
- atual consolidado: `NET_STA_DATETIME.mseed`
- o adapter RNC precisa suportar ambos

### Artifacts and reports

- relatórios operacionais em `outputs/`
- summaries com sufixo `_summary.csv`
- reports humanos em `.md`

## File Organization

- scripts executaveis mantem `main()` e `argparse`
- alguns scripts ajustam `sys.path` manualmente para importar `src/` sem instalacao do pacote
- imports costumam seguir stdlib -> terceiros -> imports locais

## Data and Schema Conventions

- `event.json` usa chaves em `snake_case`
- blocos principais observados:
  - `sisbra`
  - `fdsn`
  - `picks`
  - `picks_skipped`
  - `waveform_download_contract`
  - `rnc_prediction`
- CSVs de auditoria tendem a carregar contexto minimo suficiente para reprocessar ou investigar (`event_id`, status, mensagem, paths relativos)

## Error Handling

- abordagem defensiva, com muitos `try/except Exception`
- helpers `_safe_float`, `_safe_int` e parse tolerante sao recorrentes
- falhas operacionais costumam virar:
  - linha em CSV de erro
  - status textual
  - `SystemExit` em CLIs

## Comments and Documentation

- docstrings no topo dos scripts explicam regras de negocio e modo de uso
- comentarios inline aparecem pouco e geralmente justificam uma decisao operacional
- `README.md` e docs em `docs/` funcionam como runbooks; `.specs/codebase/` deve refletir o baseline vivo

## Observed Style Notes

- codigo ASCII-first
- typing moderno (`list[str]`, `dict[str, Any]`, `X | None`)
- JSON persistido com `ensure_ascii=True`, `indent=2` e `sort_keys=True` na etapa RNC
