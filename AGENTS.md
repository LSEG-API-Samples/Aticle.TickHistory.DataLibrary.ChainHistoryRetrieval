# Project Guidelines

A single-notebook example that resolves historical chain constituents with the LSEG Tick History REST API and retrieves their prices with the LSEG Data Library for Python. See [README.md](README.md) for background and full setup.

## Build and Test

- Python 3.12+ with a virtual environment at `.venv` (PowerShell: `.\.venv\Scripts\Activate.ps1`).
- Install: `python -m pip install -r requirements.txt`
- `pytest` is dev-only and intentionally **not** in `requirements.txt`. Install it manually with `python -m pip install pytest`, and do not add it to `requirements.txt`.
- Test: `python -m pytest -v` from the project root. Tests run offline; DSS REST and `lseg.data` calls are mocked.

## Architecture

- [notebook/chainhistory_tickhistory_ld.ipynb](notebook/chainhistory_tickhistory_ld.ipynb) holds the whole workflow: DSS authentication, `resolve_chain_request`, `get_valid_rics`, `compare_chain_constituents`, and `ld.get_history`.
- [tests/test_chainhistory_notebook.py](tests/test_chainhistory_notebook.py) loads the notebook with `nbformat` and tests it directly. There is no separate Python module.
- [Article.md](Article.md) is the written walkthrough of the historical chain resolution and price retrieval workflow. Its content is not in the same order as the notebook: it covers constituents for both years before retrieving prices, while the notebook retrieves 2024 prices before resolving 2026 constituents.
- [images/](images/) contains the screenshots referenced by the article, including chain displays and DataFrame results.

## Conventions

- DSS credentials come from the `DSS_USERNAME` and `DSS_PASSWORD` environment variables. Never hard-code or commit credentials or tokens. Data Library settings live in `notebook/lseg-data.config.json`.
- `resolve_chain_request` returns `{chain_ric: constituents}`. Key by each result's `"Identifier"`, never by position, because chains with no history are omitted from the API's `"value"` list.
- Name variables `<instrument>_rics_<year>` and `<instrument>_history_<year>`, for example `us_10y_treasury_rics_2024` and `euro_bobl_5y_history_2026`.
- Update markdown cells when renaming variables; the prose refers to them by name.
- Keep article code examples and explanations consistent with the relevant notebook workflow. When changing article screenshots, check that image links and captions point to the correct files and results.

## Notebook and Test Coupling

- Keep helper functions as top-level `def`s in code cells. The tests extract only top-level imports and functions.
- `test_missing_dss_credentials_raises_value_error` selects cells by position (`notebook.cells[1]` imports, `notebook.cells[3]` config). If you insert or reorder cells before the config cell, update those indexes.
- The end-to-end test runs every code cell in order with mocks. New HTTP calls must use a mocked endpoint (`/Authentication/RequestToken`, `/Search/HistoricalChainResolution`, `/Authentication/InvalidateToken`) and pass `timeout=TIMEOUT`. The test asserts `timeout == 30`, so keep `TIMEOUT = 30` or update the test.
- Running notebook cells directly calls live DSS and Workspace services and needs credentials. Prefer pytest to verify changes.
