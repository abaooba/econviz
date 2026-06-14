"""Chart builders for EconViz.

Produces Plotly figures and summary statistics consumed by the Streamlit app.
"""

import pandas as pd
import plotly.graph_objects as go

from src.events import CATEGORY_STYLE

# Maps pandas frequency alias -> (tickformat, dtick) for Plotly x-axis.
_FREQ_TICK: dict[str, tuple[str, str | None]] = {
    "MS": ("%b %Y", None),
    "QS": ("%b %Y", "M3"),
    "YS": ("%Y", "M12"),
}


def _event_marker_trace(
    series: pd.Series,
    events: list[dict] | None,
    yaxis: str = "y",
    label: str | None = None,
) -> go.Scatter | None:
    """Build a Scatter of category-colored dots snapped onto the line at event dates.

    Each marker sits on the observation nearest the event date and carries the
    event headline + one-liner on hover. ``yaxis`` targets the axis to ride ("y1"/
    "y2" on a dual-axis compare chart); ``label`` prefixes the hover so a viewer
    knows which series a dot belongs to. Returns None when there's nothing to plot.
    """
    if not events or series.empty:
        return None
    ex, ey, ecolor, ecustom = [], [], [], []
    lo, hi = series.index.min(), series.index.max()
    for e in events:
        ts = pd.Timestamp(e["date"])
        if ts < lo or ts > hi:
            continue
        pos = series.index.get_indexer([ts], method="nearest")
        if len(pos) == 0 or pos[0] == -1:
            continue
        i = pos[0]
        ex.append(series.index[i])
        ey.append(float(series.iloc[i]))
        ecolor.append(CATEGORY_STYLE.get(e.get("category", ""), {}).get("color", "#666"))
        headline = f"{label} — {e['title']}" if label else e["title"]
        ecustom.append([headline, e["short"]])
    if not ex:
        return None
    return go.Scatter(
        x=ex,
        y=ey,
        mode="markers",
        name="Notable event",
        marker=dict(
            size=10,
            color=ecolor,
            symbol="circle",
            line=dict(color="white", width=1.5),
            opacity=0.95,
        ),
        customdata=ecustom,
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
        showlegend=False,
        yaxis=yaxis,
    )


def make_line_chart(
    series: pd.Series,
    title: str,
    y_label: str,
    recession_bands: list[dict],
    freq: str = "MS",
    events: list[dict] | None = None,
) -> go.Figure:
    """Build a line chart with hover tooltips and NBER recession shading.

    Recession periods are drawn as semi-transparent red vertical bands using
    add_vrect, layered below the data line. If ``events`` is provided, a small
    marker is snapped onto the line at each event's date, colored by category,
    with the event title + one-liner on hover. Passing no events yields exactly
    the same clean chart as before.
    """
    fig = go.Figure()

    if not series.empty:
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=title,
                line=dict(color="#1f77b4", width=2),
                hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}<extra></extra>",
            )
        )

    for band in recession_bands:
        fig.add_vrect(
            x0=band["start"],
            x1=band["end"],
            fillcolor="red",
            opacity=0.15,
            layer="below",
            line_width=0,
        )

    marker = _event_marker_trace(series, events)
    if marker is not None:
        fig.add_trace(marker)

    tick_fmt, dtick = _FREQ_TICK.get(freq, ("%b %Y", None))
    xaxis_cfg: dict = dict(
        title="Date",
        showgrid=True,
        gridcolor="#e5e5e5",
        tickformat=tick_fmt,
    )
    if dtick:
        xaxis_cfg["dtick"] = dtick

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=xaxis_cfg,
        yaxis_title=y_label,
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=50),
    )

    return fig


def make_comparison_chart(
    series_a: pd.Series,
    series_b: pd.Series,
    label_a: str,
    label_b: str,
    recession_bands: list[dict],
    freq: str = "MS",
    events_a: list[dict] | None = None,
    events_b: list[dict] | None = None,
) -> go.Figure:
    """Build a dual-axis line chart overlaying two economic series.

    Series A is plotted against the left y-axis (blue); series B against the
    right y-axis (orange). Both share the same x-axis. NBER recession bands
    are shaded in the background. If ``events_a``/``events_b`` are provided, each
    series gets its own category-colored markers on its own axis, with a hover
    label naming the series so the two sets stay distinguishable.
    """
    fig = go.Figure()

    if not series_a.empty:
        fig.add_trace(
            go.Scatter(
                x=series_a.index,
                y=series_a.values,
                mode="lines",
                name=label_a,
                line=dict(color="#1f77b4", width=2),
                yaxis="y1",
                hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}<extra></extra>",
            )
        )

    if not series_b.empty:
        fig.add_trace(
            go.Scatter(
                x=series_b.index,
                y=series_b.values,
                mode="lines",
                name=label_b,
                line=dict(color="#ff7f0e", width=2),
                yaxis="y2",
                hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}<extra></extra>",
            )
        )

    for band in recession_bands:
        fig.add_vrect(
            x0=band["start"],
            x1=band["end"],
            fillcolor="red",
            opacity=0.15,
            layer="below",
            line_width=0,
        )

    # Each series gets its own markers on its own axis so the dots line up with the
    # right curve; the hover label names the series to keep the two sets readable.
    for s, evs, axis, lbl in (
        (series_a, events_a, "y1", label_a),
        (series_b, events_b, "y2", label_b),
    ):
        marker = _event_marker_trace(s, evs, yaxis=axis, label=lbl)
        if marker is not None:
            fig.add_trace(marker)

    tick_fmt, dtick = _FREQ_TICK.get(freq, ("%b %Y", None))
    xaxis_cfg: dict = dict(
        title="Date",
        showgrid=True,
        gridcolor="#e5e5e5",
        tickformat=tick_fmt,
    )
    if dtick:
        xaxis_cfg["dtick"] = dtick

    fig.update_layout(
        title=dict(text=f"{label_a} vs {label_b}", font=dict(size=16)),
        xaxis=xaxis_cfg,
        yaxis=dict(
            title=dict(text=label_a, font=dict(color="#1f77b4")),
            tickfont=dict(color="#1f77b4"),
            showgrid=True,
            gridcolor="#e5e5e5",
        ),
        yaxis2=dict(
            title=dict(text=label_b, font=dict(color="#ff7f0e")),
            tickfont=dict(color="#ff7f0e"),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(l=60, r=60, t=60, b=50),
    )

    return fig


def make_summary_card(series: pd.Series, label: str) -> dict:
    """Return latest value, 1-year change, and trend arrow for a series.

    Looks back min(12, len-1) periods to compute the change so short series
    don't raise an IndexError.
    """
    if series.empty or len(series) < 2:
        return {"label": label, "latest": None, "change": None, "arrow": "—"}

    latest = float(series.iloc[-1])
    lookback = min(12, len(series) - 1)
    prior = float(series.iloc[-1 - lookback])
    change = latest - prior
    arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")

    return {"label": label, "latest": latest, "change": change, "arrow": arrow}
