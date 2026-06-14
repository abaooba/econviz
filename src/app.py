"""EconViz — Economic Indicators Dashboard

Run with:  streamlit run src/app.py
"""

import os
import sys
from datetime import date, datetime

# Add project root to sys.path so `from src.X import` resolves when
# Streamlit adds src/ (not the project root) to the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env before any src imports so FRED_API_KEY is in the environment
# when fetch.py reads it at module import time.
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import pandas as pd
import streamlit as st

from src.charts import make_comparison_chart, make_line_chart, make_summary_card
from src.events import CATEGORY_STYLE, events_in_range
from src.fetch import clip_bands_to_window, fetch_indicator, fetch_recession_bands
from src.indicators import INDICATORS
from src.transform import compute_yoy_change, resample_series

st.set_page_config(
    page_title="EconViz",
    page_icon="\U0001f4c8",
    layout="wide",
)

_API_KEY = os.getenv("FRED_API_KEY")

# ── Header ──────────────────────────────────────────────────────────────────────────────
col_title, col_ts = st.columns([4, 1])
with col_title:
    st.title("\U0001f4c8 EconViz — Economic Indicators Dashboard")
    st.caption("Powered by FRED — Federal Reserve Economic Data")
with col_ts:
    st.caption(f"Last updated  \n{datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}")

if not _API_KEY:
    st.error(
        "**FRED API key not found.**  \n"
        "Add `FRED_API_KEY=your_key` to a `.env` file in the project root, then restart the app.  \n"
        "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
    )

# ── Date-range presets ───────────────────────────────────────────────────────────────────
# One-click ranges replace the fiddly two-click calendar. Value = years back from
# today; None means all available history, "custom" reveals the manual picker.
_MIN_DATE = date(1950, 1, 1)
_RANGE_PRESETS = {"1Y": 1, "5Y": 5, "10Y": 10, "25Y": 25, "Max": None, "Custom": "custom"}
_DEFAULT_PRESET = "10Y"


def resolve_date_range() -> tuple[str, str]:
    """Render the date-range controls and return (start, end) as ISO strings.

    Quick presets cover the common cases in a single click; the 'Custom' option
    reveals the full range picker only when needed. This replaces the bare
    two-click calendar, which forced a rerun mid-selection and was hard to operate.
    """
    today = date.today()
    preset = st.segmented_control(
        "Date range",
        list(_RANGE_PRESETS),
        default=_DEFAULT_PRESET,
        key="range_preset",
    ) or _DEFAULT_PRESET

    if preset == "Custom":
        default_start = (pd.Timestamp(today) - pd.DateOffset(years=10)).date()
        custom = st.date_input(
            "Pick start and end dates",
            value=(default_start, today),
            min_value=_MIN_DATE,
            max_value=today,
            key="custom_range",
        )
        # date_input yields a length-1 tuple while only the start is chosen.
        if isinstance(custom, (list, tuple)):
            return str(custom[0]), str(custom[-1])
        return str(custom), str(custom)

    years = _RANGE_PRESETS[preset]
    if years is None:  # "Max" — all available history
        return str(_MIN_DATE), str(today)
    start = (pd.Timestamp(today) - pd.DateOffset(years=years)).date()
    return str(start), str(today)


# ── Sidebar ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")

    start_str, end_str = resolve_date_range()

    st.divider()
    st.subheader("Frequency")
    freq_label = st.radio(
        "Resample to",
        ["Monthly", "Quarterly", "Annual"],
        index=0,
        horizontal=True,
    )
    _FREQ_MAP = {"Monthly": "MS", "Quarterly": "QS", "Annual": "YS"}
    freq = _FREQ_MAP[freq_label]

    st.divider()
    st.subheader("Indicators")
    st.caption("Check an indicator to load it.")
    # Default the first indicator on so the app opens with data + insights visible
    # instead of an empty screen.
    selected = [
        name for i, name in enumerate(INDICATORS) if st.checkbox(name, value=(i == 0))
    ]

if not selected:
    st.info("\U0001f448 Select one or more indicators in the sidebar to load their data.")
    st.stop()

# ── Recession bands (shared by all charts) ───────────────────────────────────────────────────────
# Full NBER history is fetched once and cached; clip to the visible window so
# off-range shapes never stretch a chart's auto x-axis.
with st.spinner("Fetching data from FRED…"):
    recession_bands = clip_bands_to_window(
        fetch_recession_bands(start_str, end_str), start_str, end_str
    )

# ── Per-indicator metadata ───────────────────────────────────────────────────────────────────
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


_UNITS = {
    "GDP Growth (%)": "%",
    "Inflation (CPI YoY %)": "%",
    "Unemployment Rate (%)": "%",
    "Federal Funds Rate (%)": "%",
    "Consumer Sentiment": "",
}


def _to_csv_bytes(series: pd.Series, col_name: str) -> bytes:
    df = series.rename(col_name).to_frame()
    df.index.name = "date"
    return df.to_csv().encode()


def _current_read(name: str, latest, change, five_yr_avg) -> str:
    """Build a data-driven one-liner: latest value vs its 5-year average and trend."""
    if latest is None:
        return ""
    unit = _UNITS.get(name, "")
    parts = [f"the latest reading is **{latest:.2f}{unit}**"]
    if pd.notna(five_yr_avg):
        diff = latest - five_yr_avg
        if abs(diff) < 0.05:
            parts.append(f"right around its 5-year average of {five_yr_avg:.2f}{unit}")
        else:
            direction = "above" if diff > 0 else "below"
            parts.append(
                f"{abs(diff):.2f}{unit} {direction} its 5-year average of {five_yr_avg:.2f}{unit}"
            )
    if change is not None:
        if abs(change) < 0.05:
            parts.append("and roughly flat over the past year")
        else:
            verb = "up" if change > 0 else "down"
            parts.append(f"and {verb} {abs(change):.2f}{unit} over the past year")
    return ", ".join(parts) + "."


def _render_event(e: dict) -> None:
    """Render one curated event: category badge, headline, date, and explanation."""
    style = CATEGORY_STYLE.get(e["category"], {})
    when = pd.Timestamp(e["date"]).strftime("%b %Y")
    st.markdown(
        f"{style.get('emoji', '•')} **{e['title']}** · {when}  ·  _{style.get('label', '')}_"
    )
    st.markdown(f"*{e['short']}*")
    st.write(e["detail"])


# ── Tabs ──────────────────────────────────────────────────────────────────────────────────────
tabs = st.tabs(selected + ["Compare"])

for i, name in enumerate(selected):
    with tabs[i]:
        # Each indicator is fetched and cached independently, so one failing
        # never affects the others.
        try:
            with st.spinner(f"Loading {name}…"):
                raw = fetch_indicator(name, start_str, end_str)
        except Exception:
            raw = pd.Series(dtype=float)

        if raw.empty:
            if _API_KEY:
                st.warning(
                    f"Data for **{name}** could not be loaded from FRED "
                    "(temporary hiccup). Press **R** to retry."
                )
            else:
                st.warning(f"No data for **{name}** — a valid FRED API key is required.")
            continue

        # CPI is fetched as a price-level index; convert to YoY %
        series = compute_yoy_change(raw).dropna() if name == "Inflation (CPI YoY %)" else raw.dropna()
        series = resample_series(series, freq)

        # ── Metric cards ─────────────────────────────────────────────────────────────────────
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

        # ── What this measures (prominent, above the chart) ──────────────────────────────────────
        blurb = _BLURBS.get(name)
        if blurb:
            st.info(f"**What this measures** — {blurb}", icon="📘")

        # ── Chart with notable-event markers ─────────────────────────────────────────────────────
        events = events_in_range(name, start_str, end_str)
        fig = make_line_chart(
            series=series,
            title=name,
            y_label=_Y_LABELS.get(name, "Value"),
            recession_bands=recession_bands,
            freq=freq,
            events=events,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── The current read (data-driven) ───────────────────────────────────────────────────────
        read = _current_read(name, card["latest"], card["change"], five_yr_avg)
        if read:
            st.markdown(f"🔍 **The current read** — {read}")

        # ── Notable events & what they mean ──────────────────────────────────────────────────────
        if events:
            with st.expander(f"📌 Notable events & what they mean ({len(events)})", expanded=True):
                st.caption(
                    "Hand-written explanations for the biggest moves on this chart — the colored "
                    "dots above mark each one. Widen the date range (try **Max**) to surface more."
                )
                for j, e in enumerate(events):
                    _render_event(e)
                    if j < len(events) - 1:
                        st.divider()
        else:
            st.caption(
                "ℹ️ No curated events fall in this window — widen the date range (e.g. **Max**) to "
                "see historic episodes like the 1980s Volcker shock or the 2008 financial crisis."
            )

        # ── CSV export ──────────────────────────────────────────────────────────────────────────────
        series_id = INDICATORS[name]
        st.download_button(
            label=f"Download {name} data (.csv)",
            data=_to_csv_bytes(series, "value"),
            file_name=f"econviz_{series_id}_{start_str}_{end_str}.csv",
            mime="text/csv",
            key=f"dl_{series_id}",
        )

# ── Compare tab ──────────────────────────────────────────────────────────────────────────────
with tabs[-1]:
    st.subheader("Compare Two Indicators")
    st.caption("Select any two indicators to overlay them on a dual-axis chart.")

    all_names = list(INDICATORS.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        choice_a = st.selectbox("Indicator A", all_names, index=0, key="compare_a")
    with col_b:
        choices_b = [n for n in all_names if n != choice_a]
        choice_b = st.selectbox("Indicator B", choices_b, index=0, key="compare_b")

    try:
        with st.spinner(f"Loading {choice_a}…"):
            raw_a = fetch_indicator(choice_a, start_str, end_str)
        with st.spinner(f"Loading {choice_b}…"):
            raw_b = fetch_indicator(choice_b, start_str, end_str)
    except Exception:
        if _API_KEY:
            st.warning("Could not load data for one or both indicators. Press **R** to retry.")
        else:
            st.warning("A valid FRED API key is required to load indicator data.")
    else:
        series_a = compute_yoy_change(raw_a).dropna() if choice_a == "Inflation (CPI YoY %)" else raw_a.dropna()
        series_b = compute_yoy_change(raw_b).dropna() if choice_b == "Inflation (CPI YoY %)" else raw_b.dropna()
        series_a = resample_series(series_a, freq)
        series_b = resample_series(series_b, freq)

        aligned_a, aligned_b = series_a.align(series_b, join="inner")
        if len(aligned_a) >= 2:
            corr = float(aligned_a.corr(aligned_b))
            st.metric(
                label=f"Pearson Correlation — {choice_a} vs {choice_b} (overlapping dates)",
                value=f"{corr:.3f}",
            )

        fig = make_comparison_chart(
            series_a=series_a,
            series_b=series_b,
            label_a=choice_a,
            label_b=choice_b,
            recession_bands=recession_bands,
            freq=freq,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Combined CSV export ───────────────────────────────────────────────────────────────────
        if not series_a.empty and not series_b.empty:
            combined = pd.DataFrame({choice_a: series_a, choice_b: series_b})
            combined.index.name = "date"
            combined_bytes = combined.to_csv().encode()
            sid_a = INDICATORS[choice_a]
            sid_b = INDICATORS[choice_b]
            st.download_button(
                label=f"Download {choice_a} + {choice_b} combined (.csv)",
                data=combined_bytes,
                file_name=f"econviz_{sid_a}_{sid_b}_{start_str}_{end_str}.csv",
                mime="text/csv",
                key="dl_compare",
            )

# ── Footer ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sourced from FRED, Federal Reserve Bank of St. Louis · fred.stlouisfed.org")
