"""Unit tests for src/transform.py."""

import pandas as pd
import pytest

from src.transform import compute_yoy_change, resample_series, resample_to_monthly


def _monthly_series(start="2020-01-01", periods=24, start_val=260.0, step=2.0):
    idx = pd.date_range(start=start, periods=periods, freq="MS")
    return pd.Series([start_val + i * step for i in range(periods)], index=idx)


class TestComputeYoyChange:
    def test_output_same_length_as_input(self):
        assert len(compute_yoy_change(_monthly_series(periods=24))) == 24

    def test_first_12_values_are_nan(self):
        result = compute_yoy_change(_monthly_series(periods=24))
        assert result.iloc[:12].isna().all()

    def test_values_after_12_are_not_nan(self):
        result = compute_yoy_change(_monthly_series(periods=24))
        assert result.iloc[12:].notna().all()

    def test_approximate_yoy_value(self):
        # start_val=260, step=2 -> month-13 value=284, month-1 value=260
        # YoY % = (284-260)/260*100 = 24/260*100 ≈ 9.231
        s = _monthly_series(start_val=260.0, step=2.0, periods=24)
        result = compute_yoy_change(s)
        expected = (2.0 * 12) / 260.0 * 100
        assert abs(result.iloc[12] - expected) < 0.01

    def test_empty_series_returns_empty(self):
        assert compute_yoy_change(pd.Series(dtype=float)).empty


class TestResampleToMonthly:
    def test_empty_series_returns_empty(self):
        assert resample_to_monthly(pd.Series(dtype=float)).empty

    def test_quarterly_produces_monthly_count(self):
        idx = pd.date_range("2020-01-01", periods=4, freq="QS")
        s = pd.Series([100.0, 101.0, 102.0, 103.0], index=idx)
        result = resample_to_monthly(s)
        expected_len = len(pd.date_range(idx[0], idx[-1], freq="MS"))
        assert len(result) == expected_len

    def test_forward_fill_within_quarter(self):
        idx = pd.date_range("2020-01-01", periods=2, freq="QS")
        s = pd.Series([100.0, 104.0], index=idx)
        result = resample_to_monthly(s)
        # Feb and Mar inherit Q1 value; Apr starts Q2
        assert result.loc["2020-02-01"] == 100.0
        assert result.loc["2020-03-01"] == 100.0
        assert result.loc["2020-04-01"] == 104.0

    def test_already_monthly_values_unchanged(self):
        idx = pd.date_range("2020-01-01", periods=12, freq="MS")
        s = pd.Series(range(12), index=idx, dtype=float)
        result = resample_to_monthly(s)
        assert len(result) == 12
        for i in range(12):
            assert result.iloc[i] == float(i)


class TestResampleSeries:
    def test_empty_returns_empty(self):
        assert resample_series(pd.Series(dtype=float), "MS").empty

    def test_monthly_to_quarterly_reduces_observations(self):
        idx = pd.date_range("2020-01-01", periods=12, freq="MS")
        s = pd.Series(range(12), index=idx, dtype=float)
        result = resample_series(s, "QS")
        assert len(result) == 4

    def test_monthly_to_annual_reduces_to_one_year(self):
        idx = pd.date_range("2020-01-01", periods=12, freq="MS")
        s = pd.Series(range(12), index=idx, dtype=float)
        result = resample_series(s, "YS")
        assert len(result) == 1

    def test_takes_last_value_in_period(self):
        # Monthly series Jan-Mar; quarterly resample should take March (index 2)
        idx = pd.date_range("2020-01-01", periods=3, freq="MS")
        s = pd.Series([10.0, 20.0, 30.0], index=idx)
        result = resample_series(s, "QS")
        assert result.iloc[0] == 30.0

    def test_already_at_target_freq_unchanged(self):
        idx = pd.date_range("2020-01-01", periods=4, freq="QS")
        s = pd.Series([1.0, 2.0, 3.0, 4.0], index=idx)
        result = resample_series(s, "QS")
        assert len(result) == 4
        assert list(result.values) == [1.0, 2.0, 3.0, 4.0]
