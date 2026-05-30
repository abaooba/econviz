"""Data transformation helpers for EconViz.

Converts raw FRED series to analysis-ready forms before charting.
"""

import pandas as pd


def compute_yoy_change(series: pd.Series) -> pd.Series:
    """Convert a level series to year-over-year percentage change.

    Computes pct_change(12) * 100 to turn CPI levels into the inflation rate
    as a YoY percentage. The first 12 observations become NaN.
    """
    return series.pct_change(periods=12) * 100


def resample_to_monthly(series: pd.Series) -> pd.Series:
    """Resample a lower-frequency series to monthly via forward-fill.

    Aligns quarterly GDP data with monthly indicators for side-by-side charting.
    Does nothing to an empty series.
    """
    if series.empty:
        return series
    monthly_index = pd.date_range(
        start=series.index[0], end=series.index[-1], freq="MS"
    )
    return series.reindex(monthly_index).ffill()
