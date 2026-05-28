# Phase 2 — Core Data Layer

**Objective:** Build a clean, tested data-fetching module that retrieves 5 key economic indicators from FRED, transforms them into analysis-ready Pandas DataFrames, and caches results to avoid redundant API calls.

**Estimated duration:** 3 days

---

## Tasks

1. **Define the indicator registry**
   - Create `src/indicators.py`
   - Define a dictionary mapping friendly names to FRED series IDs:
     ```python
     INDICATORS = {
         "GDP Growth (%)": "A191RL1Q225SBEA",
         "Inflation (CPI YoY %)": "CPIAUCSL",
         "Unemployment Rate (%)": "UNRATE",
         "Federal Funds Rate (%)": "FEDFUNDS",
         "Consumer Sentiment": "UMCSENT",
     }
     ```
   - Also define the NBER recession series ID: `"USREC"`

2. **Build the fetch module**
   - Create `src/fetch.py`
   - Write `fetch_series(series_id, start_date, end_date) -> pd.Series` using `fredapi.Fred`
   - Write `fetch_all_indicators(start_date, end_date) -> dict[str, pd.Series]` that loops the registry
   - Write `fetch_recession_bands(start_date, end_date) -> list[dict]` that converts the USREC binary series into a list of `{"start": date, "end": date}` dicts for chart shading
   - Handle `fredapi` exceptions gracefully — return empty Series and log a warning rather than crashing

3. **Add Streamlit caching**
   - Wrap `fetch_all_indicators` and `fetch_recession_bands` with `@st.cache_data(ttl=3600)` so data refreshes at most once per hour

4. **Write a data transform helper**
   - Create `src/transform.py`
   - Write `compute_yoy_change(series: pd.Series) -> pd.Series` for CPI (convert level to YoY % change)
   - Write `resample_to_monthly(series: pd.Series) -> pd.Series` to normalize quarterly data (GDP) to monthly frequency via forward-fill

5. **Unit tests**
   - Create `tests/test_fetch.py` and `tests/test_transform.py`
   - Test `compute_yoy_change` with a synthetic Series — assert output length, nulls, and approximate values
   - Test `resample_to_monthly` with quarterly stub data — assert monthly frequency output
   - Test `fetch_recession_bands` output structure (list of dicts with "start"/"end" keys) using a mocked FRED response

---

## Dependencies

- Phase 1 complete (venv, `.env`, `fredapi` installed)
- FRED API key set in `.env` ⚠️ — tests that call the live API are skipped if key is absent

## Items Requiring Ares's Input

- **FRED API key** (same as Phase 1) — must be in `.env` for live data tests to run

---

## Definition of Done

- `src/indicators.py`, `src/fetch.py`, `src/transform.py` all exist and importable
- `fetch_all_indicators` returns a dict of 5 non-empty Series when key is set
- `fetch_recession_bands` returns a list of dicts with correct keys
- All transform unit tests pass without API key
- No unhandled exceptions when FRED API key is missing
