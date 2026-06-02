"""EconViz — Economic Indicators Dashboard

Run with:  streamlit run src/app.py
"""

import os
import sys
from datetime import date

# Add project root to sys.path so `from src.X import` resolves when
# Streamlit adds src/ (not the project root) to the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env before any src imports so FRED_API_KEY is in the environment
# when fetch.py reads it at module import time.
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import pandas as pd
import streamlit as st

from src.charts import make_line_chart, make_summary_card
from src.fetch import fetch_all_indicators, fetch_recession_bands
from src.indicators import INDICATORS
from src.transform import compute_yoy_change

st.set_page_config(
    page_title="EconViz",
    page_icon="📈",
    layout="wide",
)

_API_KEY = os.getenv("FRED_API_KEY")

st.title("📈 EconViz — Economic Indicators Dashboard")
st.caption("Live U.S. macroeconomic data powered by the Federal Reserve (FRED)")

if not _API_KEY:
    st.error(
        "**FRED API key not found.**  \n"
        "Add `FRED_API_KEY=your_key` to a `.env` file in the project root, then restart the app.  \n"
        "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
    )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")

    today = date.today()
    default_start = today.replace(year=today.year - 10)

    date_range = st.date_input(
        "Date range",
        value=(default_start, today),
        min_value=date(1950, 1, 1),
        max_value=today,
    )

    st.divider()
    st.subheader("Indicators")
    selected = [name for name in INDICATORS if st.checkbox(name, value=True)]

if not selected:
    st.info("Select at least one indicator in the sidebar to view charts.")
    st.stop()

# st.date_input returns a tuple when a range is active; fall back gracefully
# if the user has only picked the start date (tuple of length 1)
if isinstance(date_range, (list, tuple)):
    start_str = str(date_range[0])
    end_str = str(date_range[1]) if len(date_range) > 1 else str(date_range[0])
else:
    start_str = end_str = str(date_range)

# ── Data fetch ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching data from FRED…"):
    all_data = fetch_all_indicators(start_str, end_str)
    recession_bands = fetch_recession_bands(start_str, end_str)

# ── Per-indicator metadata ─────────────────────────────────────────────────────
_Y_LABELS = {
    "GDP Growth (%)": "% (Annual Rate)",
    "Inflation (CPI YoY %)": "YoY %",
    "Unemployment Rate (%)": "%",
    "Federal Funds Rate (%)": "%",
    "Consumer Sentiment": "Index",
}

_BLURBS = {
    "GDP Growth (%)": (
        "Real GDP growth measures how fast the economy is expanding after adjusting for inflation. "
        "Two consecutive quarters of negative growth constitute a technical recession — the shaded "
        "bands on this chart mark officially declared NBER recessions."
    ),
    "Inflation (CPI YoY %)": (
        "CPI year-over-year tracks average consumer price changes relative to the same month a year prior. "
        "The Fed targets ~2%; sustained readings above 4–5% historically trigger rate-hike cycles "
        "that slow borrowing and investment."
    ),
    "Unemployment Rate (%)": (
        "The unemployment rate is the share of the labor force actively seeking but unable to find work. "
        "Readings above 6% signal a weakening labor market; below 4% often means wages are rising "
        "faster than productivity."
    ),
    "Federal Funds Rate (%)": (
        "The federal funds rate is the overnight rate the Fed sets to steer monetary policy. "
        "Higher rates cool inflation by making borrowing costlier; lower rates stimulate growth "
        "by making credit cheap."
    ),
    "Consumer Sentiment": (
        "The University of Michigan Consumer Sentiment Index gauges household confidence in economic conditions. "
        "Because consumer spending drives ~70% of U.S. GDP, sharp drops in sentiment often lead "
        "economic slowdowns by one to two quarters."
    ),
}

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(selected + ["Compare"])

for i, name in enumerate(selected):
    with tabs[i]:
        raw = all_data.get(name, pd.Series(dtype=float))

        if raw.empty:
            if _API_KEY:
                st.warning(
                    f"Data for **{name}** could not be loaded from FRED. "
                    "Check your API key or try refreshing the page."
                )
            else:
                st.warning(f"No data for **{name}** — a valid FRED API key is required.")
            continue

        # CPI is fetched as a price-level index; convert to YoY %
        series = compute_yoy_change(raw).dropna() if name == "Inflation (CPI YoY %)" else raw.dropna()

        # ── Metric cards ──────────────────────────────────────────────────────
        card = make_summary_card(series, name)

        cutoff_5yr = pd.Timestamp(end_str) - pd.DateOffset(years=5)
        five_yr_avg = series[series.index >= cutoff_5yr].mean()

        col1, col2, col3 = st.columns(3)
        latest_fmt = f"{card['latest']:.2f}" if card["latest"] is not None else "N/A"
        change_fmt = f"{card['change']:+.2f}" if card["change"] is not None else None
        avg_fmt = f"{five_yr_avg:.2f}" if pd.notna(five_yr_avg) else "N/A"

        col1.metric("Latest Value", latest_fmt, delta=change_fmt)
        col2.metric("1-Year Change", change_fmt or "N/A")
        col3.metric("5-Year Average", avg_fmt)

        # ── Chart ─────────────────────────────────────────────────────────────
        fig = make_line_chart(
            series=series,
            title=name,
            y_label=_Y_LABELS.get(name, "Value"),
            recession_bands=recession_bands,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Plain-English blurb ───────────────────────────────────────────────
        blurb = _BLURBS.get(name)
        if blurb:
            st.caption(blurb)

# Compare tab — built in Phase 4
with tabs[-1]:
    st.info(
        "**Compare** — overlay any two indicators on a dual-axis chart with a "
        "correlation metric.  \nThis tab will be built in Phase 4."
    )
