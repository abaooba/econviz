"""Unit tests for src/fetch.py.

@st.cache_data is neutralized by conftest.py before this module loads.
All tests mock fetch_series to avoid live FRED API calls.
"""

import pandas as pd
import pytest
from unittest.mock import patch

from src.fetch import (
    clip_bands_to_window,
    fetch_indicator,
    fetch_recession_bands,
    fetch_series,
)


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


class TestFetchIndicatorSlicing:
    """fetch_indicator slices a once-fetched full series in memory."""

    @staticmethod
    def _full_series() -> pd.Series:
        idx = pd.date_range("2010-01-01", periods=120, freq="MS")
        return pd.Series(range(120), index=idx, dtype=float)

    def test_slices_to_requested_window(self):
        with patch("src.fetch._load_full_series", return_value=self._full_series()):
            out = fetch_indicator("Unemployment Rate (%)", "2012-01-01", "2012-12-31")
        assert out.index.min() >= pd.Timestamp("2012-01-01")
        assert out.index.max() <= pd.Timestamp("2012-12-31")
        assert len(out) == 12

    def test_raises_when_window_has_no_data(self):
        with patch("src.fetch._load_full_series", return_value=self._full_series()):
            with pytest.raises(RuntimeError):
                fetch_indicator("Unemployment Rate (%)", "1990-01-01", "1990-12-31")


class TestClipBandsToWindow:
    def test_keeps_and_clamps_band_starting_before_window(self):
        bands = [{"start": pd.Timestamp("2007-12-01"), "end": pd.Timestamp("2009-06-01")}]
        out = clip_bands_to_window(bands, "2008-01-01", "2026-01-01")
        assert len(out) == 1
        assert out[0]["start"] == pd.Timestamp("2008-01-01")  # clamped up to window start
        assert out[0]["end"] == pd.Timestamp("2009-06-01")

    def test_clamps_band_extending_past_window_end(self):
        bands = [{"start": pd.Timestamp("2020-01-01"), "end": pd.Timestamp("2030-01-01")}]
        out = clip_bands_to_window(bands, "2015-01-01", "2025-01-01")
        assert out[0]["end"] == pd.Timestamp("2025-01-01")

    def test_drops_band_entirely_outside_window(self):
        bands = [{"start": pd.Timestamp("1990-01-01"), "end": pd.Timestamp("1991-01-01")}]
        assert clip_bands_to_window(bands, "2000-01-01", "2010-01-01") == []
