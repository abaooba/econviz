"""Unit tests for src/fetch.py.

@st.cache_data is neutralized by conftest.py before this module loads.
All tests mock fetch_series to avoid live FRED API calls.
"""

import pandas as pd
import pytest
from unittest.mock import patch

from src.fetch import fetch_recession_bands, fetch_series


def _usrec(pattern: list) -> pd.Series:
    """Build a synthetic USREC binary series from a 0/1 list."""
    idx = pd.date_range("2020-01-01", periods=len(pattern), freq="MS")
    return pd.Series(pattern, index=idx, dtype=float)


class TestFetchSeriesNoKey:
    def test_returns_empty_series_without_api_key(self):
        with patch("src.fetch.os.getenv", return_value=None):
            result = fetch_series("UNRATE", "2020-01-01", "2020-12-31")
        assert isinstance(result, pd.Series)
        assert result.empty


class TestFetchRecessionBands:
    def test_empty_fetch_returns_empty_list(self):
        with patch("src.fetch.fetch_series", return_value=pd.Series(dtype=float)):
            assert fetch_recession_bands("2000-01-01", "2001-01-01") == []

    def test_no_recession_in_series_returns_empty_list(self):
        with patch("src.fetch.fetch_series", return_value=_usrec([0, 0, 0, 0])):
            assert fetch_recession_bands("2000-01-01", "2001-01-01") == []

    def test_single_recession_band_correct_dates(self):
        fake = _usrec([0, 0, 1, 1, 1, 0, 0])
        with patch("src.fetch.fetch_series", return_value=fake):
            result = fetch_recession_bands("2000-01-01", "2001-01-01")
        assert len(result) == 1
        assert result[0]["start"] == fake.index[2]
        assert result[0]["end"] == fake.index[5]

    def test_two_separate_recession_bands(self):
        fake = _usrec([1, 0, 1, 1, 0])
        with patch("src.fetch.fetch_series", return_value=fake):
            result = fetch_recession_bands("2000-01-01", "2001-01-01")
        assert len(result) == 2

    def test_recession_open_at_end_of_series(self):
        fake = _usrec([0, 1, 1])
        with patch("src.fetch.fetch_series", return_value=fake):
            result = fetch_recession_bands("2000-01-01", "2001-01-01")
        assert len(result) == 1
        assert result[0]["end"] == fake.index[-1]

    def test_output_is_list_of_dicts_with_start_end_keys(self):
        fake = _usrec([1, 0])
        with patch("src.fetch.fetch_series", return_value=fake):
            result = fetch_recession_bands("2000-01-01", "2001-01-01")
        assert isinstance(result, list)
        for band in result:
            assert isinstance(band, dict)
            assert set(band.keys()) == {"start", "end"}
