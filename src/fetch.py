"""Data-fetching functions for EconViz.

Pulls series from the FRED API. Returns empty Series on error instead of crashing,
so the dashboard degrades gracefully when the API key is absent or a request fails.

Why we fetch full history and slice in memory
---------------------------------------------
FRED returns the same underlying series no matter the requested window, so caching
by (series_id, start, end) made every date-range change a fresh API call. Under quick
range-switching that bursts requests and trips FRED's rate limit, which surfaces in
the UI as "temporary hiccup" errors. Instead we download each series' full history
*once*, cache it by id (and persist to disk so it survives the free tier's sleep/wake
cycle), then slice locally — so changing the range costs zero API calls.
"""

import logging
import os
import random
import time
from datetime import date

import pandas as pd
import streamlit as st

from src.config import get_fred_api_key
from src.indicators import INDICATORS, RECESSION_SERIES_ID

logger = logging.getLogger(__name__)

# These macro indicators update at most daily (most monthly/quarterly), so a long
# TTL avoids needless refetching — and every refetch is a chance to hit a transient
# FRED failure.
_CACHE_TTL = 6 * 60 * 60  # 6 hours

# Lower bound for "all available history"; FRED clamps it to each series' real start.
_FULL_HISTORY_START = "1900-01-01"

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


# One Fred client per API key. Reusing it keeps the underlying HTTPS connection warm
# across calls instead of re-handshaking on every request — a common source of flaky
# SSL/connection errors when many series are fetched in quick succession.
_CLIENTS: dict[str, object] = {}


def _get_client(api_key: str):
    client = _CLIENTS.get(api_key)
    if client is None:
        from fredapi import Fred

        client = Fred(api_key=api_key)
        _CLIENTS[api_key] = client
    return client


def fetch_series(
    series_id: str, start_date: str, end_date: str, retries: int = 3
) -> pd.Series:
    """Fetch a single FRED series between start_date and end_date.

    Retries transient failures with exponential backoff plus jitter. Returns an
    empty Series if the API key is missing or every attempt fails.
    """
    api_key = get_fred_api_key()
    if not api_key:
        logger.warning("FRED_API_KEY not set — returning empty Series for %s", series_id)
        return pd.Series(dtype=float)
    for attempt in range(retries + 1):
        try:
            fred = _get_client(api_key)
            return fred.get_series(
                series_id, observation_start=start_date, observation_end=end_date
            )
        except Exception as exc:
            logger.warning(
                "Failed to fetch %s (attempt %d/%d): %s",
                series_id, attempt + 1, retries + 1, exc,
            )
            if attempt < retries:
                # Exponential backoff (~0.5s, 1s, 2s) with jitter so concurrent
                # reruns don't retry in lockstep and re-trip a rate limit.
                time.sleep(0.5 * (2 ** attempt) + random.uniform(0, 0.4))
    return pd.Series(dtype=float)


@st.cache_data(ttl=_CACHE_TTL, show_spinner=False, persist="disk")
def _load_full_series(series_id: str) -> pd.Series:
    """Download a FRED series' entire available history, cached by id alone.

    Raises on an empty result so the failure is NOT cached (st.cache_data skips
    caching when the function raises) — the next run retries instead of being stuck
    with an empty series for the whole TTL. Callers slice this to the requested
    window in memory, so changing the date range never re-hits the API.
    """
    series = fetch_series(series_id, _FULL_HISTORY_START, date.today().isoformat())
    if series.empty:
        raise RuntimeError(f"No data returned for series {series_id}")
    return series.sort_index()


def fetch_indicator(name: str, start_date: str, end_date: str) -> pd.Series:
    """Fetch one indicator by display name, sliced to [start_date, end_date].

    The full series is fetched once and cached; this slice is a cheap in-memory
    operation, so switching date ranges does not trigger new API calls. Raises if
    the indicator has no observations in the requested window.
    """
    full = _load_full_series(INDICATORS[name])
    sliced = full.loc[start_date:end_date]
    if sliced.empty:
        raise RuntimeError(f"No data for {name} between {start_date} and {end_date}")
    return sliced


def fetch_all_indicators(start_date: str, end_date: str) -> dict[str, pd.Series]:
    """Fetch every registered indicator, each sliced to the requested window.

    Degrades per-series: one indicator failing yields an empty Series for that key
    rather than failing the whole batch.
    """
    out: dict[str, pd.Series] = {}
    for name, sid in INDICATORS.items():
        try:
            out[name] = _load_full_series(sid).loc[start_date:end_date]
        except Exception:
            out[name] = pd.Series(dtype=float)
    return out


@st.cache_data(ttl=_CACHE_TTL, show_spinner=False, persist="disk")
def _load_recession_flags() -> pd.Series:
    """USREC binary recession flags (full history), cached.

    Returns empty on failure rather than raising — recession shading is optional
    decoration, so a hiccup here should leave the charts unshaded, not error.
    """
    return fetch_series(RECESSION_SERIES_ID, _FULL_HISTORY_START, date.today().isoformat())


def fetch_recession_bands(start_date: str, end_date: str) -> list[dict]:
    """Return NBER recession periods as a list of {start, end} date dicts.

    The USREC series is a binary 0/1 flag; this groups consecutive 1s into
    contiguous recession windows. The full series is fetched once and cached, so the
    start_date/end_date arguments no longer drive a refetch — display windowing is
    applied by the caller via clip_bands_to_window(). Returns an empty list if the
    API key is absent or the request fails.
    """
    series = _load_recession_flags()
    if series.empty:
        return []
    bands: list[dict] = []
    in_recession = False
    band_start = None
    for date_, val in series.items():
        if val == 1 and not in_recession:
            in_recession = True
            band_start = date_
        elif val == 0 and in_recession:
            in_recession = False
            bands.append({"start": band_start, "end": date_})
    if in_recession:
        bands.append({"start": band_start, "end": series.index[-1]})
    return bands


def clip_bands_to_window(bands: list[dict], start_date: str, end_date: str) -> list[dict]:
    """Keep only recession bands overlapping [start_date, end_date], clamped to it.

    Clamping matters because chart shapes outside the plotted x-range can stretch a
    Plotly auto-axis. Returning bands bounded by the window keeps shading where it
    belongs regardless of how much history fetch_recession_bands returns.
    """
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    clipped: list[dict] = []
    for band in bands:
        b_start = pd.Timestamp(band["start"])
        b_end = pd.Timestamp(band["end"])
        if b_end >= start and b_start <= end:  # overlaps the window
            clipped.append({"start": max(b_start, start), "end": min(b_end, end)})
    return clipped
