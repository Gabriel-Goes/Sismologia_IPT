# Testing Infrastructure

## Test Frameworks

- Primary framework in repository tests: `unittest` (Python stdlib)
- Plugin aggregate runner (legacy QGIS template): `nosetests` via Makefile
- Coverage hook in plugin Makefile: `--with-coverage --cover-package=.`
- No project-wide `pytest` configuration was found.

## Test Organization

### Main test location observed

- `fonte/interface/farejadorsismo/test/`

### Naming pattern

- `test_*.py` files
- Examples:
  - `test_init.py`
  - `test_qgis_environment.py`
  - `test_farejador_eventos_dockwidget.py`
  - `test_resources.py`
  - `test_translations.py`

### Supporting test utilities

- QGIS test bootstrap helpers:
  - `qgis_interface.py`
  - `utilities.py`
- Test fixture assets:
  - `tenbytenraster.asc`, `.prj`, `.qml`, etc.

## Testing Patterns Observed

### Plugin metadata and environment validation

- `test_init.py`: verifies required plugin metadata keys in `metadata.txt`.
- `test_qgis_environment.py`: checks QGIS providers and CRS parsing.

### UI smoke tests

- `test_farejador_eventos_dockwidget.py`: basic dock widget instantiation.
- `test_resources.py`: verifies icon/resource loading.

### Translation test

- `test_translations.py`: basic translator behavior check.

## Test Execution

### Plugin-level command (from Makefile)

```bash
cd fonte/interface/farejadorsismo
make test
```

Under the hood, `make test` sets QGIS-related env vars and runs:

```bash
nosetests -v --with-id --with-coverage --cover-package=.
```

### Alternative direct execution

Individual tests can be run with `python -m unittest` (if QGIS runtime env is configured).

## Test Environment Requirements

- QGIS Python runtime available in environment (`qgis.core`, `qgis.gui`, `qgis.PyQt`)
- Helper script for env setup:
  - `fonte/interface/farejadorsismo/scripts/run-env-linux.sh`
- Makefile explicitly warns about `no module named qgis.core` if env is not prepared.

## Coverage Targets

- Current numeric coverage thresholds: **not defined**.
- Enforcement gates in CI: **not found**.
- Coverage generation capability exists only in the QGIS plugin Makefile context.

## Gaps and Risks (current state)

- No automated test suite found for core pipeline modules:
  - `fonte/nucleo/*`
  - `fonte/rnc/*`
  - `fonte/analise_dados/*`
- No deterministic regression tests for CSV contracts between stages.
- Many pipeline paths depend on local file system state and external FDSN services, which complicates repeatable tests.

