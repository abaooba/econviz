"""Data-fetching functions for EconViz.

Pulls series from the FRED API. Returns empty Series on error instead of crashing,
so the dashboard degrades gracefully when the API key is absent or a request fails.
"""

import logging
import os
import time

import pandas as pd
import streamlit as st

from src.config import get_fred_api_key
from src.indicators import INDICATORS, RECESSION_SERIES_ID

logger = logging.getLogger(__name__)

# python.org macOS Python builds ship without wired-up CA certificates, so
# urllib (used internally by fredapi) raises CERTIFICATE_VERIFY_FAILED on every
# HTTPS call. Point OpenSSL at certifi's bundle so SSL verification works
# without requiring the user to run "Install Certificates.command" by hand.
try:
    import certifi

    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("SSL_CERT_DIR", os.path.dirname(certifi.where()))
except ImportError:
    logger.warning("certifi not installed — SSL verification may fail on macOS")


def fetch_series(
    series_id: str, start_date: str, end_date: str, retries: int = 2
) -> pd.Series:
    """Fetch a single FRED series between start_date and end_date.

    Retries transient failures with a short backoff. Returns an empty Series
    if the API key is missing or every attempt fails.
    """
    api_key = get_fred_api_key()
    if not api_key:
        logger.warning("FRED_API_KEY not set — returning empty Series for %s", series_id)
        return pd.Series(dtype=float)
    for attempt in range(retries + 1):
        try:
            from fredapi import Fred

            fred = Fred(api_key=api_key)
            return fred.get_series(
                series_id, observation_start=start_date, observation_end=end_date
            )
        except Exception as exc:
            logger.warning(
                "Failed to fetch %s (attempt %d/%d): %s",
                series_id, attempt + 1, retries + 1, exc,
            )
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    return pd.Series(dtype=float)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_indicator(name: str, start_date: str, end_date: str) -> pd.Series:
    """Fetch one indicator by its display name.

    Raises if the fetch comes back empty. st.cache_data does NOT cache results
    when the function raises, so a transient FRED failure is retried on the next
    run instead of being stuck as an empty (cached) result for the whole TTL.
    """
    series = fetch_series(INDICATORS[name], start_date, end_date)
    if series.empty:
        raise RuntimeError(f"No data returned for {name}")
    return series


@st.cache_data(ttl=3600)
def fetch_all_indicators(start_date: str, end_date: str) -> dict[str, pd.Series]:
    """Fetch all registered economic indicators from FRED."""
    return {
        name: fetch_series(sid, start_date, end_date)
        for name, sid in INDICATORS.items()
    }


@st.cache_data(ttl=3600)
def fetch_recession_bands(start_date: str, end_date: str) -> list[dict]:
    """Fetch NBER recession periods as a list of {start, end} date dicts.

    The USREC series is a binary 0/1 flag. This function groups consecutive 1s
    into contiguous recession windows for chart shading.
    Returns an empty list if the API key is absent or the request fails.
    """
    series = fetch_series(RECESSION_SERIES_ID, start_date, end_date)
    if series.empty:
        return []
    bands: list[dict] = []
    in_recession = False
    band_start = None
    for date, val in series.items():
        if val == 1 and not in_recession:
            in_recession = True
            band_start = date
        elif val == 0 and in_recession:
            in_recession = False
            bands.append({"start": band_start, "end": date})
    if in_recession:
        bands.append({"start": band_start, "end": series.index[-1]})
    return bands
