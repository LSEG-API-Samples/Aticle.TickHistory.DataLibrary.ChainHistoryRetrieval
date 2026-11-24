# Getting Historical Chain Data with LSEG Tick History REST API and LSEG Data Library for Python

- Last Updated: November 2026
- Language: Python
- Prerequisites: DataScope Select credentials and permission for the Tick History REST API; Workspace or Data Platform access for the LSEG Data Library for Python

## Overview

A chain RIC identifies a group of related instrument names, not their values. For example, a chain may contain the constituents of a market index like the Dow Jones or the list of strike prices on a particular option contract. 

Chain membership can change over time as instruments are listed or delisted. Bond chains are one example: exchanges periodically update which bonds meet the maturity and coupon criteria for delivery. Newly issued Treasuries may be added, while bonds that fall below the minimum remaining maturity may be removed.

Examples:
- **0#TYc1=DLV**: CBoT 10-Year US Treasury Note
- **0#FGBMc1=DLV**: Eurex Euro-Bobl (5-year German Govt Bond)
- **0#JGBc1=DLV**: Osaka Exchange 10-Year Japanese Government Bond

The [LSEG Data Library for Python](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python) offers a convenient way to expand a chain using its `Chain` object. The object returns a chain's *current constituents which you can then use with the library's other methods. 

The question is, how can we get the chain constituents for a specific time?

## The Solution: LSEG Tick History - REST API.

The [LSEG Tick History - REST API](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api) provides access to more than 30 years of historical intraday market data, including trades, quotes and market depth across 580+ venues and contributors through HTTP REST API. Its `/Search/HistoricalChainResolution` endpoint lets developers resolve current and past chain constituents, including inactive, historical-only instruments.

- [Tutorial 15: Historical Chain Constituents Search](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorial-15-historical-chain-constituents-search)

Once you have the constituents for the period you need, you can retrieve their historical data using Tick History, the Data Library (every editions), or another LSEG API, such as the [Data Platform APIs (RDP)](https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis).

#### Note

The Tick History REST API can also be used for the entire workflow. See the [Tick History REST API tutorials](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorials-introduction) for details. This example focuses on developers who use the Data Library for Python as their primary API.

---

## Project Structure and Included Notebooks

- [notebook/chainhistory_tickhistory_ld.ipynb](notebook/chainhistory_tickhistory_ld.ipynb): Resolves historical constituents of the `0#TYc1=DLV` Treasury and `0#FGBMc1=DLV` Bond chains for two date ranges, compares the results, and retrieves sample weekly bid and ask history using the LSEG Data Library for Python.
- [notebook/lseg-data.config.json](notebook/lseg-data.config.json): LSEG Data Library session configuration.
- [Article.md](Article.md): Written walkthrough of the workflow.
- [images/](images/): Screenshots used in the article.
- [tests/](tests/): Offline tests for the notebook.
- [requirements.txt](requirements.txt): Python dependencies.
- [AGENTS.md](AGENTS.md): Project guidance for coding agents.
- [.github/copilot-instructions.md](.github/copilot-instructions.md): GitHub Copilot instructions referencing the project guidance.

---

## Prerequisites

1. DataScope Select credentials and permission to access the Tick History REST API
2. Workspace or Data Platform access for the LSEG Data Library for Python
3. Python 3.12 or later
4. Network access to LSEG services

Contact your LSEG Account Manager or CSM team to request API access.



---

## Project Setup

1. Create and activate a virtual environment

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

Run these commands *after activating the virtual environment*:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you also want to run the automated test suite, install `pytest` manually alongside `requirements.txt`:

```powershell
python -m pip install pytest
```

3. Configure DSS credentials

Set the DSS Username and password to your OS environment variable named `DSS_USERNAME` and `DSS_PASSWORD`. Alternatively, change the following code to your DSS credential.

```python
#DSS_USERNAME = os.environ.get("DSS_USERNAME")
#DSS_PASSWORD = os.environ.get("DSS_PASSWORD")

DSS_USERNAME = "Your DSS Username"
DSS_PASSWORD = "Your DSS Password"
```

4. Configure Data Library credential

See [Data Library for Python - QuickStart Guide](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python/quick-start) page for more detail.

5. Run the notebook

Open the prefer notebook in JupyterLab or VS Code and run the cells in order.

```powershell
cd \notebook
jupyter lab trth_chainhistory_session.ipynb
```

---

## Running Tests

The automated test suite in `tests/test_chainhistory_notebook.py` validates notebook syntax, helper functions (`resolve_chain_request`, `get_valid_rics`, and `compare_chain_constituents`), and the end-to-end workflow using mocked DSS REST and LSEG Data Library responses (no live credentials required).

`pytest` is not pinned in `requirements.txt`—install it manually in your activated `.venv` alongside `requirements.txt`:

```powershell
python -m pip install pytest
```

Then run the test suite from the project root:

```powershell
python -m pytest -v
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `lseg-data` | LSEG Data Library for Python — market data access |
| `jupyterlab` | Interactive notebook environment |

See `requirements.txt` for pinned versions.

**Note**: The `pytest` is a development-only testing tool, so it is not listed in `requirements.txt` file.

---

## License

See [LICENSE.md](LICENSE.md).

---

## Reference

You can find more detail regarding the Data Library and Python Asyncio from the following resources:

- [LSEG Tick History - REST API](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api) on the [LSEG Developer Community](https://developers.lseg.com/) website
- [LSEG Tick History - REST API Tutorials](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorials-introduction)
- [LSEG Data Library for Python](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python) 
- [Data Library for Python - Quickstart Guide](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python/quick-start)
- [Data Library for Python Examples on GitHub](https://github.com/LSEG-API-Samples/Example.DataLibrary.Python) repository

For any question related to this example or Data Library, please use the Developers Community [Q&A Forum](https://community.developers.lseg.com/).