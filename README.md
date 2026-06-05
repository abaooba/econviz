# EconViz — Economic Indicators Dashboard

An interactive Python dashboard that pulls live macroeconomic data from the [Federal Reserve's FRED API](https://fred.stlouisfed.org/) and visualizes key U.S. economic indicators — GDP growth, CPI inflation, unemployment, the federal funds rate, and consumer sentiment — in a clean, browser-based UI. Built to demonstrate real API integration, a clean data-pipeline architecture, and end-to-end cloud deployment.

**[Live Demo →](#)** *(link updated after deployment)*

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Dashboard UI | Streamlit |
| Data fetching | `fredapi` |
| Data manipulation | Pandas |
| Charting | Plotly |
| Secrets | python-dotenv (local) / Streamlit Secrets (cloud) |
| Deployment | Streamlit Cloud (free tier) |
| Version control | Git / GitHub |

---

## Features

- **Live FRED data** — Five macroeconomic series fetched on load and cached for 1 hour to avoid rate-limit issues
- **Interactive time-series charts** — Zoom, pan, and hover-tooltip Plotly charts
- **Recession shading** — NBER recession periods automatically overlaid on every chart
- **Dual-axis comparison** — Overlay any two indicators with a Pearson correlation metric
- **Frequency toggle** — Switch between Monthly, Quarterly, and Annual views
- **CSV export** — Download any indicator or comparison dataset with one click

---

## How to Run Locally

**1. Clone the repo**

```bash
git clone https://github.com/abaooba/econviz.git
cd econviz
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Get a free FRED API key**

1. Create a free account at [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/)
2. Visit the [API key page](https://fred.stlouisfed.org/docs/api/api_key.html) and request a key — approved instantly

**5. Set your API key**

Create a `.env` file at the project root:

```
FRED_API_KEY=your_key_here
```

**6. Run the app**

```bash
streamlit run src/app.py
```

The app opens at `http://localhost:8501`.

---

## Project Structure

```
econviz/
├── src/
│   ├── app.py          # Streamlit application entry point
│   ├── charts.py       # Plotly chart builders (line, dual-axis, summary card)
│   ├── config.py       # API key loader (.env + Streamlit Secrets fallback)
│   ├── fetch.py        # FRED data fetching with retry logic and caching
│   ├── indicators.py   # FRED series ID registry
│   └── transform.py    # Data transformation helpers (YoY change, resampling)
├── tests/
│   ├── test_fetch.py
│   └── test_transform.py
├── conftest.py         # pytest fixtures (mocks Streamlit cache decorators)
├── requirements.txt
├── .env                # Not committed — holds your FRED_API_KEY locally
└── README.md
```

---

## License

MIT
