"""Chart builders for EconViz.

Produces Plotly figures and summary statistics consumed by the Streamlit app.
"""

import pandas as pd
import plotly.graph_objects as go


def make_line_chart(
    series: pd.Series,
    title: str,
    y_label: str,
    recession_bands: list[dict],
) -> go.Figure:
    """Build a line chart with hover tooltips and NBER recession shading.

    Recession periods are drawn as semi-transparent red vertical bands using
    add_vrect, layered below the data line.
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

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title=y_label,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
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
) -> go.Figure:
    """Build a dual-axis line chart overlaying two economic series.

    Series A is plotted against the left y-axis (blue); series B against the
    right y-axis (orange). Both share the same x-axis. NBER recession bands
    are shaded in the background.
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

    fig.update_layout(
        title=dict(text=f"{label_a} vs {label_b}", font=dict(size=16)),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#e5e5e5"),
        yaxis=dict(
            title=label_a,
            titlefont=dict(color="#1f77b4"),
            tickfont=dict(color="#1f77b4"),
            showgrid=True,
            gridcolor="#e5e5e5",
        ),
        yaxis2=dict(
            title=label_b,
            titlefont=dict(color="#ff7f0e"),
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
