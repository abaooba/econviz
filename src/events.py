"""Curated registry of notable economic events for EconViz.

Each entry is a hand-written explanation of a discrepancy or abnormality visible
in one indicator's chart — the spikes, crashes, and policy shifts a viewer is
most likely to ask "what happened there?" about. The dashboard anchors a small
marker at each event's date and shows the explanation on demand.

Schema (per entry):
    indicator : display name, must match a key in INDICATORS
    date      : "YYYY-MM-DD" anchor for the chart marker
    title     : short headline
    short     : one-line summary (marker hover + list subtitle)
    detail    : 2–4 sentence pre-written explanation
    category  : "crisis" | "policy" | "milestone"
"""

import pandas as pd

# Marker / badge styling per category. Muted on purpose so events annotate the
# line without dominating it.
CATEGORY_STYLE: dict[str, dict] = {
    "crisis": {"color": "#d62728", "emoji": "🔴", "label": "Crisis"},
    "policy": {"color": "#e8810c", "emoji": "🟠", "label": "Policy shift"},
    "milestone": {"color": "#2ca02c", "emoji": "🟢", "label": "Milestone"},
}


EVENTS: list[dict] = [
    # ── Unemployment Rate ────────────────────────────────────────────────────
    {
        "indicator": "Unemployment Rate (%)",
        "date": "1982-11-01",
        "title": "Volcker recession peak (10.8%)",
        "short": "Hit 10.8% — a post-war record until 2020",
        "detail": (
            "To break double-digit inflation, Fed Chair Paul Volcker pushed interest rates to "
            "record highs in the early 1980s. The deliberate squeeze tipped the economy into a "
            "deep recession, and unemployment peaked at 10.8% in late 1982 — the highest since "
            "the 1940s. It was the price paid to reset inflation expectations."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Unemployment Rate (%)",
        "date": "2009-10-01",
        "title": "Great Recession peak (10.0%)",
        "short": "Peaked at 10.0% after the financial crisis",
        "detail": (
            "The 2008 financial crisis and ensuing Great Recession destroyed roughly 8.7 million "
            "jobs. Unemployment climbed from 5% in early 2008 to a peak of 10.0% in October 2009, "
            "and the recovery was slow — it took until 2015 to return to pre-crisis levels."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Unemployment Rate (%)",
        "date": "2020-02-01",
        "title": "50-year low (3.5%)",
        "short": "3.5% — a 50-year low, just before COVID",
        "detail": (
            "On the eve of the pandemic, unemployment sat at 3.5% — the lowest in half a century — "
            "capping a decade-long expansion. Within two months it would be the highest on record, "
            "one of the most violent swings in the history of the series."
        ),
        "category": "milestone",
    },
    {
        "indicator": "Unemployment Rate (%)",
        "date": "2020-04-01",
        "title": "COVID-19 shock (14.7%)",
        "short": "Leapt to 14.7% in weeks as lockdowns hit",
        "detail": (
            "When pandemic lockdowns began in March 2020, hiring froze and layoffs exploded. "
            "Unemployment rocketed from 3.5% in February to 14.7% in April 2020 — the highest "
            "since the series began in 1948. Unusually, the rebound was also fast: rehiring "
            "brought it back near 5% within about 18 months."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Unemployment Rate (%)",
        "date": "2023-04-01",
        "title": "Tight labor market holds",
        "short": "Held below 4% despite aggressive rate hikes",
        "detail": (
            "Even as the Fed raised rates at the fastest pace in 40 years, the labor market stayed "
            "remarkably tight, with unemployment holding below 4% for the longest stretch since the "
            "1960s. Economists watched for a 'soft landing' — cooling inflation without a jobs crash."
        ),
        "category": "milestone",
    },
    # ── Inflation (CPI YoY %) ────────────────────────────────────────────────
    {
        "indicator": "Inflation (CPI YoY %)",
        "date": "1980-03-01",
        "title": "Great Inflation peak (~14.6%)",
        "short": "Peaked near 14.6% during the second oil shock",
        "detail": (
            "The 1979 Iranian Revolution sent oil prices soaring, and a decade of loose policy had "
            "un-anchored inflation expectations. CPI inflation peaked at about 14.6% in early 1980. "
            "Taming it required the Volcker Fed to drive interest rates to ~19% and accept a severe "
            "recession."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Inflation (CPI YoY %)",
        "date": "2009-07-01",
        "title": "Deflation scare",
        "short": "Turned negative — a rare bout of falling prices",
        "detail": (
            "As the financial crisis crushed demand and oil prices collapsed, year-over-year CPI "
            "briefly went negative in 2009 — the first deflation in over half a century. Falling "
            "prices sound good but can be dangerous: households delay purchases and debts grow "
            "heavier in real terms."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Inflation (CPI YoY %)",
        "date": "2015-04-01",
        "title": "Oil-crash disinflation",
        "short": "Near zero as oil prices crashed",
        "detail": (
            "A global oil glut roughly halved crude prices in 2014–15, dragging headline inflation "
            "down to around zero. With prices barely rising, the Fed held rates near zero longer "
            "than expected before its first post-crisis hike in December 2015."
        ),
        "category": "milestone",
    },
    {
        "indicator": "Inflation (CPI YoY %)",
        "date": "2022-06-01",
        "title": "40-year high (9.1%)",
        "short": "Hit 9.1% — the highest since 1981",
        "detail": (
            "Pandemic stimulus, snarled supply chains, and a 2022 energy spike after Russia's "
            "invasion of Ukraine drove inflation to 9.1% in June 2022 — the highest since 1981. "
            "The Fed responded with its fastest rate-hiking cycle in four decades, and inflation "
            "cooled steadily through 2023."
        ),
        "category": "crisis",
    },
    # ── GDP Growth (%) ───────────────────────────────────────────────────────
    {
        "indicator": "GDP Growth (%)",
        "date": "2008-10-01",
        "title": "Great Recession trough",
        "short": "Shrank ~8% annualized at the crisis trough",
        "detail": (
            "As the financial system seized up in late 2008, output collapsed — Q4 2008 GDP "
            "contracted at roughly an 8% annual rate, the worst quarter of the Great Recession. "
            "The downturn erased trillions in wealth and took years to fully recover from."
        ),
        "category": "crisis",
    },
    {
        "indicator": "GDP Growth (%)",
        "date": "2020-04-01",
        "title": "COVID collapse",
        "short": "Collapsed ~30% annualized as the economy shut",
        "detail": (
            "Pandemic lockdowns produced the deepest quarterly contraction on record: GDP fell at "
            "roughly a 30% annual rate in Q2 2020. It was also the shortest recession ever — the "
            "next quarter rebounded at a record pace as the economy reopened."
        ),
        "category": "crisis",
    },
    {
        "indicator": "GDP Growth (%)",
        "date": "2020-07-01",
        "title": "Record rebound",
        "short": "Record ~+35% annualized bounce-back",
        "detail": (
            "After the spring 2020 collapse, reopening produced the largest quarterly expansion "
            "ever recorded — about a 35% annual rate in Q3 2020. The V-shaped bounce recovered "
            "much, though not all, of the lost output within months."
        ),
        "category": "milestone",
    },
    {
        "indicator": "GDP Growth (%)",
        "date": "2022-04-01",
        "title": "The recession that wasn't",
        "short": "Two negative quarters sparked a recession debate",
        "detail": (
            "GDP shrank in both Q1 and Q2 2022, meeting the popular 'two quarters' rule of thumb "
            "for a recession. But with unemployment near 50-year lows, the official NBER arbiter "
            "declined to call it one — a vivid lesson that no single number defines a recession."
        ),
        "category": "milestone",
    },
    # ── Federal Funds Rate (%) ───────────────────────────────────────────────
    {
        "indicator": "Federal Funds Rate (%)",
        "date": "1981-06-01",
        "title": "Volcker peak (~19%)",
        "short": "Peaked near 19% to break inflation",
        "detail": (
            "Under Chair Paul Volcker, the Fed drove its policy rate to nearly 19% in 1981 — by far "
            "the highest in its history — to crush double-digit inflation. The shock worked but "
            "triggered back-to-back recessions and 10.8% unemployment, establishing the Fed's "
            "modern credibility as an inflation-fighter."
        ),
        "category": "policy",
    },
    {
        "indicator": "Federal Funds Rate (%)",
        "date": "2008-12-01",
        "title": "Zero-rate era begins",
        "short": "Slashed to ~0% for the first time ever",
        "detail": (
            "In December 2008 the Fed cut rates to effectively zero for the first time ever and "
            "held them there for seven years. With conventional ammunition exhausted, it turned to "
            "'quantitative easing' — buying bonds to push down long-term rates and revive lending."
        ),
        "category": "policy",
    },
    {
        "indicator": "Federal Funds Rate (%)",
        "date": "2020-03-01",
        "title": "COVID emergency cut",
        "short": "Emergency cut back to ~0% within days",
        "detail": (
            "As COVID-19 hit in March 2020, the Fed slashed rates to near zero in two emergency "
            "moves outside its scheduled meetings and relaunched massive bond-buying. The goal was "
            "to keep credit flowing while the economy was in free-fall."
        ),
        "category": "policy",
    },
    {
        "indicator": "Federal Funds Rate (%)",
        "date": "2023-01-01",
        "title": "Fastest hikes in 40 years",
        "short": "Raised from ~0% to ~5.3% to fight inflation",
        "detail": (
            "To fight 9% inflation, the Fed raised rates from near zero to about 5.3% between March "
            "2022 and mid-2023 — the steepest, fastest tightening since the Volcker era. Markets "
            "braced for a recession that, notably, did not immediately arrive."
        ),
        "category": "policy",
    },
    # ── Consumer Sentiment ───────────────────────────────────────────────────
    {
        "indicator": "Consumer Sentiment",
        "date": "2008-11-01",
        "title": "Financial-crisis collapse",
        "short": "Crashed to ~55 in the financial crisis",
        "detail": (
            "As markets cratered and unemployment surged, household confidence collapsed to around "
            "55 in late 2008 — among the lowest readings in decades. Sentiment tends to lead "
            "spending, so the plunge foreshadowed the deep consumer pullback of 2009."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Consumer Sentiment",
        "date": "2020-04-01",
        "title": "Pandemic plunge",
        "short": "Plunged as the pandemic hit",
        "detail": (
            "Confidence fell sharply in spring 2020 as lockdowns and mass layoffs took hold. "
            "Unusually, generous stimulus and a fast labor-market rebound helped sentiment recover "
            "more quickly than after a typical recession."
        ),
        "category": "crisis",
    },
    {
        "indicator": "Consumer Sentiment",
        "date": "2022-06-01",
        "title": "All-time low (~50)",
        "short": "Hit ~50 — the lowest in the survey's history",
        "detail": (
            "Even with unemployment near record lows, the bite of 9% inflation and surging gas "
            "prices drove consumer sentiment to about 50 in June 2022 — the lowest in the index's "
            "~70-year history. It showed how powerfully rising prices erode confidence even in a "
            "strong job market."
        ),
        "category": "crisis",
    },
]


def events_for(indicator: str) -> list[dict]:
    """Return all curated events for one indicator, sorted by date."""
    matches = [e for e in EVENTS if e["indicator"] == indicator]
    return sorted(matches, key=lambda e: e["date"])


def events_in_range(indicator: str, start: str, end: str) -> list[dict]:
    """Return this indicator's events whose date falls within [start, end].

    Bounds are inclusive. `start`/`end` may be any date string pandas can parse.
    """
    lo = pd.Timestamp(start)
    hi = pd.Timestamp(end)
    return [e for e in events_for(indicator) if lo <= pd.Timestamp(e["date"]) <= hi]
