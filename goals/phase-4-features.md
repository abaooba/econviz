# Phase 4 — Features

**Objective:** Add the dual-axis comparison chart, CSV export, and responsive polish that elevate EconViz from a basic dashboard to a polished portfolio piece.

**Estimated duration:** 3 days

---

## Tasks

1. **Dual-axis comparison chart**
   - In `src/charts.py`, write `make_comparison_chart(series_a, series_b, label_a, label_b, recession_bands) -> plotly.Figure`
     - Left y-axis for series A, right y-axis for series B (different colors)
     - Both series on the same x-axis with recession shading
     - Legend clearly identifies each series
   - Add a "Compare" tab in `src/app.py`:
     - Two dropdowns: "Indicator A" and "Indicator B"
     - Renders the comparison chart when both are selected
     - Shows a correlation coefficient (`pandas.Series.corr`) as a metric card

2. **CSV export**
   - In each indicator tab, add a `st.download_button` that exports the displayed Series as CSV
   - Button label: "Download [Indicator Name] data (.csv)"
   - Filename format: `econviz_<series_id>_<start>_<end>.csv`
   - In the Compare tab, export both series merged into a single DataFrame

3. **Date range and frequency controls**
   - Add a "Frequency" radio button in the sidebar: `Monthly` / `Quarterly` / `Annual`
   - Resample all series to the selected frequency before rendering (use `resample_to_monthly` from Phase 2 as the base, then further resample)
   - Update chart x-axis tick format to match selected frequency

4. **Layout polish**
   - Add a top-of-page header section: app title, subtitle ("Powered by FRED — Federal Reserve Economic Data"), and a last-updated timestamp
   - Ensure all charts use `use_container_width=True` and look good at 1280px and 1440px wide
   - Add a footer: "Data sourced from FRED, Federal Reserve Bank of St. Louis"

---

## Dependencies

- Phase 3 complete (full dashboard with individual charts)
- No new packages needed

## Items Requiring Ares's Input

- None for this phase

---

## Definition of Done

- Compare tab renders a dual-axis chart for any two-indicator selection
- Correlation coefficient displayed on compare tab
- CSV download works for individual and combined exports
- Frequency toggle correctly resamples and re-renders all charts
- App looks polished at standard desktop widths
