# Phase 3 — Dashboard UI

**Objective:** Build the main Streamlit dashboard with a sidebar for controls, individual chart pages per indicator, and recession period shading on every chart.

**Estimated duration:** 3 days

---

## Tasks

1. **App layout structure**
   - Update `src/app.py` with:
     - Page config: wide layout, title "EconViz", favicon 📈
     - Sidebar: date range picker (default: last 10 years), indicator multi-select checkboxes
     - Main area: tabbed layout — one tab per selected indicator, plus a "Compare" tab (built in Phase 4)
   - Use `st.spinner("Fetching data from FRED...")` while data loads

2. **Chart builder module**
   - Create `src/charts.py`
   - Write `make_line_chart(series, title, y_label, recession_bands) -> plotly.Figure`
     - Line chart with hover tooltips showing exact date + value
     - Recession periods rendered as semi-transparent red vertical bands using `add_vrect`
     - Clean styling: white background, gridlines, axis labels
   - Write `make_summary_card(series, label) -> dict` returning latest value, 1-year change, and trend arrow (↑/↓)

3. **Individual indicator pages**
   - For each selected indicator, render:
     - A summary row: 3 `st.metric` cards (latest value, 1-year change, 5-year average)
     - The Plotly line chart via `st.plotly_chart(fig, use_container_width=True)`
     - A brief 2-sentence plain-English interpretation below the chart (hardcoded per indicator — e.g. "Unemployment above 6% typically signals a weakening labor market.")

4. **Error state handling**
   - If FRED API key is missing: show a prominent `st.error` banner with instructions to add the key
   - If a specific series fails to fetch: show `st.warning` for that tab only, not crash the whole app

---

## Dependencies

- Phase 2 complete (`src/fetch.py`, `src/transform.py`, `src/indicators.py`)
- `plotly` installed

## Items Requiring Ares's Input

- None for this phase — no new keys or external accounts needed

---

## Definition of Done

- `streamlit run src/app.py` renders without errors (with or without API key)
- Each selected indicator shows: 3 metric cards + a Plotly chart + recession shading
- Sidebar date range picker correctly filters all charts
- App degrades gracefully when API key is absent (error banner, no crash)
