"""Data-fetching functions for EconViz.

Pulls series from the FRED API. Returns empty Series on error instead of crashing,
so the dashboard degrades gracefully when the API key is absent or a request fails.
"""

import logging
import os

import pandas as pd

from src.indicators import INDICATORS

logger = logging.getLogger(__name__)

_API_KEY = os.getenv("FRED_API_KEY")


def fetch_series(series_id: str, start_date: str, end_date: str) -> pd.Series:
    """Fetch a single FRED series between start_date and end_date.

    Returns an empty Series if the API key is missing or the request fails.
    """
    if not _API_KEY:
        logger.warning("FRED_API_KEY not set — returning empty Series for %s", series_id)
        return pd.Series(dtype=float)
    try:
        from fredapi import Fred  # noqa: PLC0415

        fred = Fred(api_key=_API_KEY)
        return fred.get_series(
            series_id, observation_start=start_date, observation_end=end_date
        )
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", series_id, exc)
        return pd.Series(dtype=float)


def fetch_all_indicators(start_date: str, end_date: str) -> dict[str, pd.Series]:
    """Fetch all registered economic indicators from FRED."""
    return {
        name: fetch_series(sid, start_date, end_date)
        for name, sid in INDICATORS.items()
    }
