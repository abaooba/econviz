"""Test FRED API connectivity.

This test is skipped if FRED_API_KEY is not set in the environment.
To run: pytest tests/test_fred_connection.py -v
"""

import os
import pytest
from datetime import date, timedelta


FRED_API_KEY = os.getenv("FRED_API_KEY")
HAS_KEY = bool(FRED_API_KEY and FRED_API_KEY != "your_key_here")


@pytest.mark.skipif(not HAS_KEY, reason="FRED_API_KEY not set — skipping live API test")
def test_fred_unrate_fetch():
    """Fetch UNRATE (unemployment) for the last 12 months and verify it's non-empty."""
    from fredapi import Fred
    import pandas as pd

    fred = Fred(api_key=FRED_API_KEY)
    end = date.today()
    start = end - timedelta(days=365)

    series = fred.get_series("UNRATE", observation_start=start, observation_end=end)

    assert isinstance(series, pd.Series), "Result should be a pandas Series"
    assert len(series) > 0, "Series should not be empty"
    assert series.notna().any(), "Series should contain at least some non-NaN values"
    print(f"\nFetched {len(series)} UNRATE observations from {start} to {end}")
    print(series.tail())
