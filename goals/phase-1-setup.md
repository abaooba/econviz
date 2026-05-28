# Phase 1 — Setup

**Objective:** Scaffold the project repository, configure the Python environment, and verify that the FRED API connection works end-to-end.

**Estimated duration:** 2 days

---

## Tasks

1. **Initialize the project folder**
   - Confirm `~/Documents/Claude/Projects/econviz/` exists
   - Create subfolders: `src/`, `tests/`, `data/` (for cached CSVs), `assets/`
   - Create a `.gitignore` (ignore `.env`, `__pycache__`, `data/*.csv`, `.venv/`)

2. **Set up Python virtual environment**
   - Create a `.venv` inside the project folder: `python3 -m venv .venv`
   - Install dependencies: `streamlit`, `fredapi`, `pandas`, `plotly`, `python-dotenv`, `pytest`
   - Freeze to `requirements.txt`

3. **Configure environment variables**
   - Create a `.env` file with a placeholder: `FRED_API_KEY=your_key_here`
   - Write a `src/config.py` that loads the key via `python-dotenv` and raises a clear error if it's missing

4. **Write a FRED connectivity test**
   - Create `tests/test_fred_connection.py`
   - Test: fetch the UNRATE series (unemployment) for the last 12 months and assert the result is a non-empty Pandas Series
   - This test will be skipped if `FRED_API_KEY` is not set (use `pytest.mark.skipif`)

5. **Create a minimal Streamlit stub**
   - Create `src/app.py` with: a title ("EconViz"), a sidebar placeholder, and a static "Data will appear here" message
   - Confirm it runs: `streamlit run src/app.py`

---

## Dependencies

- Python 3.11+ installed on the system
- `pip` available
- **FRED API key** — ⚠️ *Requires Ares's input* — see Pending User Requests in CLAUDE.md

---

## Items Requiring Ares's Input

- **FRED API key**: Register for free at https://fred.stlouisfed.org/docs/api/api_key.html and place the key in `.env` as `FRED_API_KEY=<your_key>`. The connectivity test (Task 4) will not pass without this.

---

## Definition of Done

- `requirements.txt` committed
- `src/config.py` loads env var without error
- `streamlit run src/app.py` shows a page with a title
- FRED connectivity test either passes (if key is set) or skips gracefully (if key is missing)
