# EconViz — Daily Work Schedule

This file maps each calendar day to a specific set of tasks. The `project-executor` task uses this file to know exactly what to work on each session. After each day's work is done, the executor marks the day complete here.

---

## Schedule

| Day | Date | Phase | Tasks | Status |
|-----|------|-------|-------|--------|
| 1 | 2026-05-29 | Phase 1 — Setup | Init folder structure, `.gitignore`, install deps, `requirements.txt` | complete |
| 2 | 2026-05-30 | Phase 1 — Setup | `src/config.py`, FRED connectivity test, Streamlit stub (`src/app.py`) | complete |
| 3 | 2026-05-31 | Phase 2 — Data | `src/indicators.py` (indicator registry + FRED series IDs), `src/fetch.py` (fetch_series, fetch_all_indicators) | complete |
| 4 | 2026-06-01 | Phase 2 — Data | `fetch_recession_bands`, Streamlit `@st.cache_data` wrapping, `src/transform.py` | complete |
| 5 | 2026-06-02 | Phase 2 — Data | Unit tests: `tests/test_fetch.py`, `tests/test_transform.py` — all pass | complete |
| 6 | 2026-06-03 | Phase 3 — UI | Streamlit app layout: page config, sidebar (date picker, indicator checkboxes), tab structure | pending |
| 7 | 2026-06-04 | Phase 3 — UI | `src/charts.py`: `make_line_chart` with recession shading, `make_summary_card` | pending |
| 8 | 2026-06-05 | Phase 3 — UI | Individual indicator pages: metric cards + charts + plain-English blurbs + error state handling | pending |
| 9 | 2026-06-06 | Phase 4 — Features | `make_comparison_chart` (dual-axis), Compare tab in app with correlation metric | pending |
| 10 | 2026-06-07 | Phase 4 — Features | CSV export buttons (per-indicator + combined), filename formatting | pending |
| 11 | 2026-06-08 | Phase 4 — Features | Frequency radio toggle (Monthly/Quarterly/Annual), header + footer polish | pending |
| 12 | 2026-06-09 | Phase 5 — Deploy | `README.md`, docstrings + type hints on all public functions, `src/config.py` Streamlit secrets fallback | pending |
| 13 | 2026-06-10 | Phase 5 — Deploy | `.streamlit/secrets.toml` stub, final QA checklist, deploy instructions surfaced to Ares | pending |

---

## Notes for project-executor

- Each day, load this file first. Find the first row with `status: pending` — that's today's work.
- Mark the row `in_progress` at session start, `complete` at session end.
- If a day's work is blocked (e.g. missing FRED API key on Day 2), mark it `blocked`, record the blocker in CLAUDE.md Pending User Requests, and stop.
- Do NOT skip ahead to future days. One day at a time.
- If a day's tasks finish early, do cleanup/polish on that phase — do NOT start the next day's tasks.
