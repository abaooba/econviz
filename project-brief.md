# EconViz — Economic Indicators Dashboard

## Project Overview

- **Field:** Data Science / Economics / Finance
- **Folder:** `Projects/econviz/` (planning) + `abaooba/econviz` (code)
- **Status:** in_progress
- **Start Date:** 2026-05-28
- **Target Completion:** 2026-06-10

---

## Goal

Build an interactive Python dashboard that pulls live macroeconomic data from the Federal Reserve's FRED API and visualizes key U.S. economic indicators — including GDP growth, inflation (CPI), unemployment rate, and the S&P 500 — in a clean, browser-based UI. The app will let users explore trends over time, compare indicators side-by-side, and automatically highlight recession periods. By the end, it will be deployed publicly on Streamlit Cloud as a shareable portfolio piece.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Dashboard UI | Streamlit |
| Data fetching | `fredapi` (FRED API wrapper) |
| Data manipulation | Pandas |
| Charting | Plotly Express |
| Environment | python-dotenv (.env for API keys) |
| Deployment | Streamlit Cloud (free tier) |
| Version control | Git / GitHub |

---

## Key Features

1. **Live FRED data fetching** — Pull GDP, CPI, unemployment, federal funds rate, and consumer sentiment on app load (with caching to avoid hitting rate limits)
2. **Interactive time-series charts** — Plotly charts with zoom, hover tooltips, and date range sliders
3. **Recession shading** — Automatically overlay NBER recession bands on all charts
4. **Indicator comparison view** — Select any two indicators and overlay them on a dual-axis chart
5. **CSV export** — Download the displayed dataset as a CSV with one click

---

## Interview Talking Points

1. **Real API integration at scale** — "I connected to the Federal Reserve's FRED API, handling rate limits with `st.cache_data` and TTL expiry, so the dashboard stays responsive without hammering the API."
2. **Data pipeline thinking** — "I built a clean separation between data fetching, transformation, and visualization layers — so swapping in a different data source (e.g., Yahoo Finance) would require changing only the fetch module."
3. **End-to-end deployment** — "The app is live on Streamlit Cloud — I handled secrets management with `.env` locally and Streamlit's secrets store in production, which mirrors how environment config works in real engineering teams."

---

## Phases

### Phase 1 — Setup (2 days)
Set up the project repo, virtual environment, and verify FRED API connectivity.

### Phase 2 — Core Data Layer (3 days)
Build the data-fetching and caching module. Pull 5 key indicators, clean data, write unit tests.

### Phase 3 — Dashboard UI (3 days)
Build the Streamlit layout: sidebar controls, individual indicator charts with recession shading.

### Phase 4 — Features (3 days)
Add dual-axis comparison chart, date range filter, CSV export, and responsive layout polish.

### Phase 5 — Polish & Deploy (2 days)
Write README, add docstrings, deploy to Streamlit Cloud, verify secrets management, final QA.

---

## Progress Log

| Date | Phase | Summary |
|------|-------|----------|
| 2026-05-28 | Phase 1 — Setup | Created project folder structure (src/, tests/, data/, assets/), .gitignore, requirements.txt (streamlit, fredapi, pandas, plotly, python-dotenv, pytest), src/config.py (env var loader with clear error), src/app.py (Streamlit stub with title + sidebar placeholder), tests/test_fred_connection.py (skips gracefully without API key). All Phase 1 tasks complete. |
| 2026-05-30 | Phase 2 — Data (Day 3) | Created src/indicators.py (FRED series ID registry for 5 indicators + recession series) and src/fetch.py (fetch_series + fetch_all_indicators with graceful empty-Series fallback when API key absent). |
| 2026-05-30 | Phase 2 — Data (Day 4) | Added fetch_recession_bands to src/fetch.py (converts USREC binary series to list of {start, end} recession band dicts); wrapped fetch_all_indicators and fetch_recession_bands with @st.cache_data(ttl=3600); created src/transform.py with compute_yoy_change (CPI level -> YoY %) and resample_to_monthly (forward-fill quarterly GDP to monthly frequency). FRED API key blocker resolved. |
| 2026-05-31 | Phase 2 — Data (Day 5) | Added conftest.py (mocks @st.cache_data for pytest, adds root to sys.path); created tests/test_transform.py (9 assertions across compute_yoy_change and resample_to_monthly using synthetic Series); created tests/test_fetch.py (7 assertions testing fetch_series no-key fallback and fetch_recession_bands logic via mocked fetch_series). Phase 2 complete. |
| 2026-06-01 | Phase 3 — Dashboard UI | Created src/charts.py (make_line_chart with Plotly recession shading via add_vrect, make_summary_card returning latest/change/arrow); rewrote src/app.py with full Streamlit layout: wide page config, sidebar date-range picker (default 10 years) + indicator checkboxes, tabbed main area (one tab per indicator + Compare placeholder), 3 st.metric cards per indicator (latest value, 1-year change, 5-year average), Plotly line chart with recession bands, plain-English blurb per indicator, graceful API-key-absent error banner and per-tab st.warning for failed fetches. All 16 tests pass. Phase 3 complete. |
| 2026-06-02 | Phase 4 — Features (Day 9) | Added make_comparison_chart to src/charts.py (dual-axis Plotly figure: series A on left y-axis in blue, series B on right y-axis in orange, shared x-axis, recession shading); built out Compare tab in src/app.py (two indicator dropdowns, Pearson correlation metric card, dual-axis chart). All 16 tests still pass. |
| 2026-06-03 | Phase 4 — Features (Day 10) | Added CSV export to src/app.py: st.download_button in every indicator tab (filename: econviz_{series_id}_{start}_{end}.csv) and a combined export button in the Compare tab that merges both selected series into one DataFrame. Helper _to_csv_bytes added. |
| 2026-06-04 | Phase 4 — Features (Day 11) | Added resample_series(series, freq) to src/transform.py; added freq param to make_line_chart and make_comparison_chart in src/charts.py (maps MS/QS/YS to Plotly tickformat+dtick); added Frequency radio (Monthly/Quarterly/Annual) to sidebar in src/app.py with resampling applied before every chart render; replaced plain title with polished header (title + FRED subtitle + UTC timestamp column); added FRED attribution footer. 5 new test assertions for resample_series. Phase 4 complete. |

---

## Notes

- FRED API key now available — live FRED fetching is unblocked
- GitHub repo `abaooba/econviz` created and in use — Streamlit Cloud deployment needs Ares to connect it before Phase 5
- All source code commits go to `abaooba/econviz` exclusively; `claude-portfolio` holds only planning/scheduling files
