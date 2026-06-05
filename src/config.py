"""Configuration loader for EconViz.

Reads FRED_API_KEY from a .env file for local development. Falls back to
Streamlit Secrets (st.secrets) when running on Streamlit Cloud, where .env
files are not available and secrets are injected via the platform's secrets
manager.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_fred_api_key() -> str | None:
    """Return the FRED API key, checking .env first then Streamlit Secrets.

    Returns None when neither source provides a valid key so callers can
    degrade gracefully rather than raising on import.
    """
    key = os.getenv("FRED_API_KEY")
    if key and key != "your_key_here":
        return key
    try:
        import streamlit as st

        return st.secrets["FRED_API_KEY"]
    except Exception:
        return None


FRED_API_KEY: str | None = get_fred_api_key()
