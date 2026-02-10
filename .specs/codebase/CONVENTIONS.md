# Code Conventions

**Analyzed from representative files:**  
`fluxo_sismo.sh`, `fonte/nucleo/fluxo_eventos.py`, `fonte/nucleo/utils.py`, `fonte/analise_dados/pre_processa.py`, `fonte/analise_dados/pos_processa.py`, `fonte/rnc/run.py`, `fonte/rnc/prediction.py`, `fonte/interface/farejador.py`, `fonte/interface/farejadorsismo/farejadorsismo_dockwidget.py`, `fonte/relatorio-sismologia/pyscripts/tabela.py`.

## Naming Conventions

**Files**

- Predominant style: `snake_case.py`
- Examples:
  - `pre_processa.py`
  - `fluxo_eventos.py`
  - `farejadorsismo_dockwidget.py`
- Exception observed: `fonte/interface/__init__.Py` (uppercase extension).

**Functions / Methods**

- Predominant style: `snake_case`.
- Examples:
  - `iterar_eventos`
  - `read_catalogo`
  - `plot_box_by_station`
  - `spectro_extract`

**Classes**

- Predominant style: `PascalCase`.
- Examples:
  - `DualOutput`
  - `SeletorEventoApp`
  - `FarejadorDockWidget`

**Constants**

- Uppercase for globals and path/category constants.
- Examples:
  - `MSEED_DIR`, `DELIMT2`, `CAT_SNR`, `POS_PATH`, `CSV_FILE`.

## Language and Terminology

- Mixed Portuguese + English identifiers/comments are common.
- Domain words often remain Portuguese:
  - `catalogo`, `eventos`, `predito`, `comercial`, `nao comercial`.

## Code Organization in Files

- Common pattern:
  1. Header block with author/version/date
  2. Imports
  3. Global config/constants
  4. Functions/classes
  5. `main()` and `if __name__ == '__main__':`

- Sections are often marked with long delimiter comments (for example `# ----------------------------`).

## Import Patterns

- Typical order is: stdlib -> third-party -> local modules.
- The order is not fully strict or auto-formatted across all files.
- Multi-line explicit imports are frequent in UI modules (`PyQt5`, `qgis.core`).

## Type Safety / Typing

- Partial type hints used in some modules:
  - `fluxo_eventos.py` and `run.py` annotate parameters/returns.
- Most files remain dynamically typed without strict typing tooling.

## Error Handling

- Frequent use of broad `try/except Exception`.
- Common strategies:
  - print and continue loop
  - write row to error CSV
  - fallback to backup service/client
- Error propagation is usually not exception-based; status is persisted in files.

## Logging and Output Style

- Predominant runtime output is `print`.
- `logging` is present in some UI modules (`farejadorsismo_dockwidget.py`) but not unified project-wide.
- Shell pipeline logs are redirected with `tee` to `arquivos/registros/Sismo_Pipeline.log`.

## DataFrame and Data Contract Style

- Heavy use of `pandas` transformations with implicit column contracts.
- Column names are user-facing and domain-specific; examples:
  - `Event`, `Station`, `Pick Prob_Nat`, `Origem Latitude`, `Distance_Q2`.
- Contract enforcement is mostly runtime (KeyError/ValueError checks), not schema validation.

## Path Handling Conventions

- Mixed styles:
  - hardcoded relative paths (`arquivos/resultados/...`)
  - `os.path.join(...)`
  - `HOME`-based absolute defaults
- Several scripts assume repository location under `~/projetos/ClassificadorSismologico`.

## Test Conventions

- Test file naming: `test_*.py` under plugin test folder.
- Framework: `unittest` + QGIS test utilities.
- Legacy QGIS plugin Makefile still references `nosetests` for aggregate execution.

