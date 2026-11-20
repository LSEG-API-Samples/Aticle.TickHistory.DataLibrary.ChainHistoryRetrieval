"""Automated pytest suite for notebook/chainhistory_tickhistory_ld.ipynb."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, call

import lseg.data as ld
import nbformat
import pandas as pd
import pytest
import requests


# Point to the notebook file from the repository root.
NOTEBOOK_PATH = (
    Path(__file__).resolve().parents[1] / "notebook" / "chainhistory_tickhistory_ld.ipynb"
)
BASE_URL = "https://selectapi.datascope.lseg.com/RestApi/v1"


def execute_code(source, filename, namespace):
    """Compile and execute a Python snippet inside `namespace`."""
    exec(compile(source, filename, "exec"), namespace)  # pylint: disable=exec-used


# Load the notebook once per test module so every test shares the parsed cells.
@pytest.fixture(name="notebook", scope="module")
def fixture_notebook():
    """Read the Jupyter notebook as an nbformat v4 object."""
    with NOTEBOOK_PATH.open("r", encoding="utf-8") as handle:
        return nbformat.read(handle, as_version=4)


# Extract only imports and helper functions so unit tests can run without live API calls.
@pytest.fixture(name="notebook_funcs", scope="module")
def fixture_notebook_funcs(notebook):
    """Compile and return top-level imports and functions defined in the notebook."""
    namespace = {}
    for cell in notebook.cells:
        if cell.cell_type != "code" or not cell.source.strip():
            continue
        tree = ast.parse(cell.source)
        # Keep only import statements and `def ...` blocks; skip top-level API execution lines.
        selected_nodes = [
            node
            for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
        ]
        if selected_nodes:
            module = ast.Module(body=selected_nodes, type_ignores=[])
            ast.fix_missing_locations(module)
            execute_code(module, str(NOTEBOOK_PATH), namespace)
    return namespace


def make_mock_response(status_code=200, json_data=None, headers=None, text="", http_error=None):
    """Create a fake HTTP response that mimics `requests.Response`."""
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.headers = headers or {}
    response.text = text
    response.json.return_value = json_data if json_data is not None else {}
    # Raise the given HTTP error when `raise_for_status()` is called, or succeed quietly.
    response.raise_for_status.side_effect = http_error
    return response


# ---------------------------------------------------------------------------
# 1. Notebook structure and syntax checks
# ---------------------------------------------------------------------------


def test_notebook_file_exists_and_has_cells(notebook):
    """Confirm the notebook file exists on disk and contains cells."""
    assert NOTEBOOK_PATH.is_file()
    assert len(notebook.cells) > 0


def test_all_code_cells_have_valid_python_syntax(notebook):
    """Ensure every non-empty code cell parses as valid Python."""
    for index, cell in enumerate(notebook.cells, start=1):
        if cell.cell_type == "code" and cell.source.strip():
            ast.parse(cell.source, filename=f"{NOTEBOOK_PATH}#cell-{index}")

# 1a. Helper function existence checks
@pytest.mark.parametrize(
    "fn_name",
    ["resolve_chain_request", "get_valid_rics", "compare_chain_constituents"],
)
def test_expected_functions_are_defined(notebook_funcs, fn_name):
    """Check that each helper function used in the workflow is defined and callable."""
    assert fn_name in notebook_funcs
    assert callable(notebook_funcs[fn_name])


# ---------------------------------------------------------------------------
# 2. Unit tests for `resolve_chain_request`
# ---------------------------------------------------------------------------


def test_resolve_chain_request_returns_dict_by_chain_ric(notebook_funcs):
    """Verify HTTP 200 maps each chain RIC to its list of constituent records."""
    resolve_chain_request = notebook_funcs["resolve_chain_request"]
    session = MagicMock(spec=requests.Session)

    # Simulate a completed DSS response containing two resolved chains.
    api_payload = {
        "value": [
            {
                "Identifier": "0#TYc1=DLV",
                "Constituents": [
                    {"Identifier": "91282CBL4=", "IdentifierType": "Ric", "Status": "Valid"},
                    {"Identifier": "91282CCB5=", "IdentifierType": "Ric", "Status": "Valid"},
                ],
            },
            {
                "Identifier": "0#FGBMc1=DLV",
                "Constituents": [
                    {"Identifier": "DE110246=", "IdentifierType": "Ric", "Status": "Valid"},
                ],
            },
        ]
    }
    # Mock the POST request to return a 200 response with the API payload.
    session.post.return_value = make_mock_response(status_code=200, json_data=api_payload)
    # Call the function under test with the mocked session.
    result = resolve_chain_request(
        request_session=session,
        base_url=BASE_URL,
        chain_rics_list=["0#TYc1=DLV", "0#FGBMc1=DLV"],
        start="2024-05-01T00:00:00.000Z",
        end="2024-06-30T00:00:00.000Z",
        timeout=30,
    )

    # Check that the outgoing POST body matches the Tick History REST schema.
    session.post.assert_called_once_with(
        f"{BASE_URL}/Search/HistoricalChainResolution",
        json={
            "Request": {
                "ChainRics": ["0#TYc1=DLV", "0#FGBMc1=DLV"],
                "Range": {
                    "Start": "2024-05-01T00:00:00.000Z",
                    "End": "2024-06-30T00:00:00.000Z",
                },
            }
        },
        timeout=30,
    )
    assert set(result.keys()) == {"0#TYc1=DLV", "0#FGBMc1=DLV"}
    assert len(result["0#TYc1=DLV"]) == 2
    assert len(result["0#FGBMc1=DLV"]) == 1


def test_resolve_chain_request_polls_on_202_until_200(notebook_funcs, monkeypatch):
    """Verify HTTP 202 triggers polling of the `Location` URL until HTTP 200 is returned."""
    resolve_chain_request = notebook_funcs["resolve_chain_request"]
    session = MagicMock(spec=requests.Session)
    monitor_url = f"{BASE_URL}/Extractions/Monitor('job-1')"

    # First POST returns 202 (in progress), first GET still 202, second GET returns 200 (ready).
    session.post.return_value = make_mock_response(
        status_code=202,
        headers={"Location": monitor_url},
    )
    session.get.side_effect = [
        make_mock_response(status_code=202, headers={"Location": monitor_url}),
        make_mock_response(
            status_code=200,
            json_data={
                "value": [
                    {
                        "Identifier": "0#TYc1=DLV",
                        "Constituents": [
                            {
                                "Identifier": "91282CBL4=",
                                "IdentifierType": "Ric",
                                "Status": "Valid",
                            }
                        ],
                    }
                ]
            },
        ),
    ]

    # Replace `time.sleep` so the test runs instantly while still recording wait intervals.
    mock_sleep = MagicMock()
    monkeypatch.setattr(notebook_funcs["time"], "sleep", mock_sleep)

    result = resolve_chain_request(
        request_session=session,
        base_url=BASE_URL,
        chain_rics_list=["0#TYc1=DLV"],
        start="2024-05-01T00:00:00.000Z",
        end="2024-06-30T00:00:00.000Z",
        timeout=30,
    )

    assert mock_sleep.call_args_list == [call(5), call(5)]
    assert session.get.call_args_list == [
        call(monitor_url, timeout=30),
        call(monitor_url, timeout=30),
    ]
    assert len(result["0#TYc1=DLV"]) == 1


@pytest.mark.parametrize(
    ("api_json", "expected"),
    [
        # Empty `value` list (e.g., chain has no history) should return `{}`.
        ({"value": []}, {}),
        # Missing `Constituents` key inside a chain object should default to `[]`.
        ({"value": [{"Identifier": "0#TYc1=DLV"}]}, {"0#TYc1=DLV": []}),
    ],
)
def test_resolve_chain_request_handles_empty_or_partial_payloads(
    notebook_funcs, api_json, expected
):
    """Ensure empty or incomplete API payloads do not raise KeyError or IndexError."""
    resolve_chain_request = notebook_funcs["resolve_chain_request"]
    session = MagicMock(spec=requests.Session)
    session.post.return_value = make_mock_response(status_code=200, json_data=api_json)

    result = resolve_chain_request(
        request_session=session,
        base_url=BASE_URL,
        chain_rics_list=["0#TYc1=DLV"],
        start="2024-05-01T00:00:00.000Z",
        end="2024-06-30T00:00:00.000Z",
        timeout=30,
    )

    assert result == expected


def test_resolve_chain_request_wraps_request_errors(notebook_funcs):
    """Confirm network/HTTP errors from `requests` are raised as a clear `RuntimeError`."""
    resolve_chain_request = notebook_funcs["resolve_chain_request"]
    session = MagicMock(spec=requests.Session)
    http_err = requests.exceptions.HTTPError("401 Unauthorized")
    session.post.return_value = make_mock_response(status_code=401, http_error=http_err)

    with pytest.raises(RuntimeError, match="Historical chain resolution request failed") as exc_info:
        resolve_chain_request(
            request_session=session,
            base_url=BASE_URL,
            chain_rics_list=["0#TYc1=DLV"],
            start="2024-05-01T00:00:00.000Z",
            end="2024-06-30T00:00:00.000Z",
            timeout=30,
        )

    # Preserve the original `HTTPError` as the chained cause for easier debugging.
    assert exc_info.value.__cause__ is http_err


# ---------------------------------------------------------------------------
# 3. Unit tests for `get_valid_rics`
# ---------------------------------------------------------------------------


def test_get_valid_rics_filters_only_active_ric_items(notebook_funcs):
    """Keep only constituent items where Status is 'Valid' and IdentifierType is 'Ric'."""
    get_valid_rics = notebook_funcs["get_valid_rics"]
    constituents = {
        "0#TYc1=DLV": [
            {"Identifier": "91282CBL4=", "Status": "Valid", "IdentifierType": "Ric"},
            {"Identifier": "OLD_BOND=", "Status": "NotFound", "IdentifierType": "Ric"},
            {"Identifier": "US91282CBL46", "Status": "Valid", "IdentifierType": "Isin"},
            {"Identifier": "91282CCB5=", "Status": "Valid", "IdentifierType": "Ric"},
        ]
    }

    assert get_valid_rics(constituents, "0#TYc1=DLV") == ["91282CBL4=", "91282CCB5="]


def test_get_valid_rics_returns_empty_list_when_none_qualify(notebook_funcs):
    """Return an empty list when no records meet both Status and IdentifierType filters."""
    get_valid_rics = notebook_funcs["get_valid_rics"]
    constituents = {
        "0#TYc1=DLV": [
            {"Identifier": "OLD_BOND=", "Status": "Historical", "IdentifierType": "Ric"},
        ]
    }

    assert get_valid_rics(constituents, "0#TYc1=DLV") == []


# ---------------------------------------------------------------------------
# 4. Unit tests for `compare_chain_constituents`
# ---------------------------------------------------------------------------


def test_compare_chain_constituents_groups_rows_and_prints_counts(notebook_funcs, capsys):
    """Verify summary counts and row ordering (`Removed` -> `Unchanged` -> `Added`)."""
    compare_chain_constituents = notebook_funcs["compare_chain_constituents"]
    rics_2024 = ["B_RIC=", "A_RIC=", "C_RIC="]
    rics_2026 = ["C_RIC=", "E_RIC=", "D_RIC="]

    df = compare_chain_constituents(rics_2024, rics_2026)
    printed_summary = capsys.readouterr().out.strip()

    assert printed_summary == "2024: 3 | 2026: 3 | Removed: 2, Unchanged: 1, Added: 2"
    assert df.index.name == "RIC"
    assert list(df.columns) == ["2024", "2026", "Status"]
    # Within each status group, RICs should be sorted alphabetically.
    assert list(df.index) == ["A_RIC=", "B_RIC=", "C_RIC=", "D_RIC=", "E_RIC="]
    assert df.loc["A_RIC="].to_dict() == {"2024": "✓", "2026": "—", "Status": "Removed"}
    assert df.loc["C_RIC="].to_dict() == {"2024": "✓", "2026": "✓", "Status": "Unchanged"}
    assert df.loc["D_RIC="].to_dict() == {"2024": "—", "2026": "✓", "Status": "Added"}


def test_compare_chain_constituents_handles_empty_lists(notebook_funcs):
    """Verify empty inputs return an empty DataFrame with the expected columns and index."""
    compare_chain_constituents = notebook_funcs["compare_chain_constituents"]

    df = compare_chain_constituents([], [])

    assert df.empty
    assert df.index.name == "RIC"
    assert list(df.columns) == ["2024", "2026", "Status"]


# ---------------------------------------------------------------------------
# 5. End-to-end notebook execution tests (with mocked APIs)
# ---------------------------------------------------------------------------


def test_missing_dss_credentials_raises_value_error(notebook, monkeypatch):
    """Ensure the credential check cell stops early when DSS env vars are missing."""
    monkeypatch.delenv("DSS_USERNAME", raising=False)
    monkeypatch.delenv("DSS_PASSWORD", raising=False)

    namespace = {}
    # Run the imports cell, then run the configuration cell that checks credentials.
    execute_code(notebook.cells[1].source, str(NOTEBOOK_PATH), namespace)
    with pytest.raises(
        ValueError, match="Please set DSS_USERNAME and DSS_PASSWORD environment variables."
    ):
        execute_code(notebook.cells[3].source, str(NOTEBOOK_PATH), namespace)


def test_full_notebook_executes_end_to_end_with_mocked_services(notebook, monkeypatch):
    """Run every code cell in order using mocked DSS REST and LSEG Data Library calls."""
    monkeypatch.setenv("DSS_USERNAME", "test-user")
    monkeypatch.setenv("DSS_PASSWORD", "test-password")

    # Fake DSS responses for authentication, 2024/2026 chain resolution, and token logout.
    chain_2024_response = {
        "value": [
            {
                "Identifier": "0#TYc1=DLV",
                "Constituents": [
                    {"Identifier": f"UST24_{i}=", "Status": "Valid", "IdentifierType": "Ric"}
                    for i in range(8)
                ],
            },
            {
                "Identifier": "0#FGBMc1=DLV",
                "Constituents": [
                    {"Identifier": "DE110246=", "Status": "Valid", "IdentifierType": "Ric"},
                    {"Identifier": "DE110247=", "Status": "Valid", "IdentifierType": "Ric"},
                ],
            },
        ]
    }
    chain_2026_response = {
        "value": [
            {
                "Identifier": "0#TYc1=DLV",
                "Constituents": [
                    {"Identifier": f"UST26_{i}=", "Status": "Valid", "IdentifierType": "Ric"}
                    for i in range(7)
                ],
            },
            {
                "Identifier": "0#FGBMc1=DLV",
                "Constituents": [
                    {"Identifier": "DE103073=", "Status": "Valid", "IdentifierType": "Ric"},
                ],
            },
        ]
    }

    def fake_post(url, json=None, timeout=None):
        """Fake POST request handler for DSS endpoints."""
        assert timeout == 30
        if url.endswith("/Authentication/RequestToken"):
            return make_mock_response(status_code=200, json_data={"value": "mock-dss-token"})
        if url.endswith("/Search/HistoricalChainResolution"):
            start_date = json["Request"]["Range"]["Start"]
            payload = (
                chain_2024_response if start_date.startswith("2024") else chain_2026_response
            )
            return make_mock_response(status_code=200, json_data=payload)
        if url.endswith("/Authentication/InvalidateToken"):
            return make_mock_response(status_code=200, text="")
        raise AssertionError(f"Unexpected POST URL: {url}")

    mock_session = MagicMock()
    mock_session.headers = {}
    mock_session.post.side_effect = fake_post
    monkeypatch.setattr(requests, "Session", lambda: mock_session)

    # Mock LSEG Data Library session and historical pricing calls.
    sample_history_df = pd.DataFrame({"BID": [99.1, 99.2], "ASK": [99.3, 99.4]})
    mock_open_session = MagicMock()
    mock_get_history = MagicMock(return_value=sample_history_df)
    mock_close_session = MagicMock()
    monkeypatch.setattr(ld, "open_session", mock_open_session)
    monkeypatch.setattr(ld, "get_history", mock_get_history)
    monkeypatch.setattr(ld, "close_session", mock_close_session)

    # Execute all non-empty code cells sequentially in a shared notebook namespace.
    namespace = {}
    for index, cell in enumerate(notebook.cells, start=1):
        if cell.cell_type == "code" and cell.source.strip():
            execute_code(cell.source, f"{NOTEBOOK_PATH}#cell-{index}", namespace)

    # Verify key notebook outputs and session cleanup calls.
    assert namespace["token"] == "mock-dss-token"
    assert mock_session.headers["Authorization"] == "Token mock-dss-token"
    assert len(namespace["us_10y_treasury_rics_2024"]) == 8
    assert namespace["euro_bobl_5y_rics_2024"] == ["DE110246=", "DE110247="]
    assert len(namespace["us_10y_treasury_rics_2026"]) == 7
    assert namespace["euro_bobl_5y_rics_2026"] == ["DE103073="]
    assert namespace["us_10y_treasury_history_2024"] is sample_history_df
    assert namespace["euro_bobl_5y_history_2024"] is sample_history_df
    assert namespace["us_10y_treasury_history_2026"] is sample_history_df
    assert namespace["euro_bobl_5y_history_2026"] is sample_history_df
    mock_open_session.assert_called_once()
    assert mock_get_history.call_count == 4
    mock_close_session.assert_called_once()
