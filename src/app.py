"""EconViz — Economic Indicators Dashboard

Entry point for the Streamlit app.
Run with: streamlit run src/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="EconViz — Economic Indicators Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 EconViz — Economic Indicators Dashboard")
st.caption("Live U.S. macroeconomic data powered by the Federal Reserve (FRED)")

# Sidebar placeholder
with st.sidebar:
    st.header("Controls")
    st.info("Indicator selection and date range filters will appear here in Phase 3.")

# Main content placeholder
st.divider()
st.markdown("### Data will appear here")
st.write(
    "Charts for GDP, CPI, Unemployment, Federal Funds Rate, and Consumer Sentiment "
    "will load here once the data layer is complete (Phase 2)."
)
