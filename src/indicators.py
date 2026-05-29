"""Economic indicator registry for EconViz.

Maps friendly display names to FRED series IDs.
"""

INDICATORS: dict[str, str] = {
    "GDP Growth (%)": "A191RL1Q225SBEA",
    "Inflation (CPI YoY %)": "CPIAUCSL",
    "Unemployment Rate (%)": "UNRATE",
    "Federal Funds Rate (%)": "FEDFUNDS",
    "Consumer Sentiment": "UMCSENT",
}

RECESSION_SERIES_ID = "USREC"
