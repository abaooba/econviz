"""Configuration loader for EconViz.

Reads environment variables from a .env file in the project root.
Raises a clear error if FRED_API_KEY is missing.
"""

import os
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY or FRED_API_KEY == "your_key_here":
    raise EnvironmentError(
        "FRED_API_KEY is not set. "
        "Register for a free key at https://fred.stlouisfed.org/docs/api/api_key.html "
        "and add it to a .env file in the project root:\n"
        "  FRED_API_KEY=your_key_here"
    )
