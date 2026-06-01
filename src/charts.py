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
