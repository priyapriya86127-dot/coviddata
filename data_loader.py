"""Load COVID dashboard datasets from the Excel workbook."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

SHEET_SUMMARY = "Global Summary"
SHEET_COUNTRIES = "Country Data"
SHEET_TRENDS = "Monthly Trends"
SHEET_VAX = "Vaccination"
SHEET_NEWS = "News Updates"

# ISO 3166-1 alpha-2 for flag CDN
COUNTRY_FLAG_CODE = {
    "USA": "us",
    "India": "in",
    "Brazil": "br",
    "France": "fr",
    "Germany": "de",
    "UK": "gb",
    "Russia": "ru",
    "Japan": "jp",
    "Italy": "it",
    "Canada": "ca",
}

# Plotly choropleth country names
PLOTLY_LOCATION = {
    "USA": "United States",
    "India": "India",
    "Brazil": "Brazil",
    "France": "France",
    "Germany": "Germany",
    "UK": "United Kingdom",
    "Russia": "Russia",
    "Japan": "Japan",
    "Italy": "Italy",
    "Canada": "Canada",
}

KPI_THEMES = [
    "purple",
    "green",
    "blue",
    "red",
    "yellow",
]


def get_workbook_path() -> Path:
    return _resolve_workbook_path()


def _resolve_workbook_path() -> Path:
    env = os.environ.get("COVID19_XLSX")
    if env:
        p = Path(env)
        if p.is_file():
            return p
    here = Path(__file__).resolve().parent
    candidates = [
        here / "data" / "covid19.xlsx",
        here.parent / "covid19.xlsx",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "covid19.xlsx not found. Place it in covid/data/ or set COVID19_XLSX."
    )


def _fmt_compact(n: float | int) -> str:
    x = float(n)
    ax = abs(x)
    if ax >= 1e9:
        return f"{x / 1e9:.2f}B"
    if ax >= 1e6:
        return f"{x / 1e6:.2f}M"
    if ax >= 1e3:
        return f"{x / 1e3:.2f}K"
    return f"{int(x):,}"


def _normalize_int(val: Any) -> int | float:
    if pd.isna(val):
        return 0
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return 0


def load_dashboard_payload() -> dict[str, Any]:
    path = get_workbook_path()
    xl = pd.ExcelFile(path)

    summary_df = pd.read_excel(xl, SHEET_SUMMARY)
    metrics_order = summary_df["Metric"].tolist()
    values = [_normalize_int(v) for v in summary_df["Value"].tolist()]
    daily = [str(summary_df.iloc[i].get("Daily Change", "") or "") for i in range(len(summary_df))]

    summary = []
    for i, metric in enumerate(metrics_order):
        v = values[i] if i < len(values) else 0
        summary.append(
            {
                "metric": str(metric),
                "value_raw": v,
                "value_display": _fmt_compact(v) if isinstance(v, (int, float)) else str(v),
                "daily_change": daily[i] if i < len(daily) else "",
                "theme": KPI_THEMES[i % len(KPI_THEMES)],
            }
        )

    trends_df = pd.read_excel(xl, SHEET_TRENDS)
    trend_labels = [str(x) for x in trends_df["Month"].tolist()]
    cases = [float(x) for x in trends_df["Cases"].tolist()]
    recovered_t = [float(x) for x in trends_df["Recovered"].tolist()]
    deaths_t = [float(x) for x in trends_df["Deaths"].tolist()]

    total_cases = values[0] if values else 1
    active_cases = values[1] if len(values) > 1 else 1
    ratio_active = float(active_cases) / float(total_cases) if total_cases else 0.024
    vax_total = float(values[4]) if len(values) > 4 else 13.34e9
    n = len(cases)
    if n <= 1:
        vaccinated_line = [vax_total * 0.95, vax_total]
    else:
        v0 = vax_total * 0.92
        vaccinated_line = [v0 + (vax_total - v0) * i / (n - 1) for i in range(n)]

    active_line = [c * ratio_active for c in cases]
    sparklines = [cases, active_line, recovered_t, deaths_t, vaccinated_line]

    for i, row in enumerate(summary):
        row["sparkline"] = sparklines[i] if i < len(sparklines) else cases

    countries_df = pd.read_excel(xl, SHEET_COUNTRIES)
    countries = []
    for _, r in countries_df.iterrows():
        name = str(r["Country"]).strip()
        countries.append(
            {
                "country": name,
                "flag_code": COUNTRY_FLAG_CODE.get(name, "").lower() or "xx",
                "plotly_location": PLOTLY_LOCATION.get(name, name),
                "total_cases": _normalize_int(r.get("Total Cases")),
                "deaths": _normalize_int(r.get("Deaths")),
                "recovered": _normalize_int(r.get("Recovered")),
                "vaccinated_pct": int(_normalize_int(r.get("Vaccinated (%)"))),
            }
        )

    vax_df = pd.read_excel(xl, SHEET_VAX)
    vaccination = {}
    for _, r in vax_df.iterrows():
        cat = str(r["Category"])
        vaccination[cat] = _normalize_int(r.get("Count"))

    pop = float(vaccination.get("Total Population", 1))
    fully = float(vaccination.get("Fully Vaccinated", 0))
    pct_fully = round(100.0 * fully / pop, 1) if pop else 0.0

    news_df = pd.read_excel(xl, SHEET_NEWS)
    news = []
    for _, r in news_df.iterrows():
        d = r.get("Date")
        if pd.notna(d):
            if hasattr(d, "strftime"):
                date_s = d.strftime("%Y-%m-%d")
            else:
                date_s = str(d)[:10]
        else:
            date_s = ""
        news.append(
            {
                "date": date_s,
                "headline": str(r.get("Headline", "")),
                "source": str(r.get("Source", "")),
            }
        )

    map_locations = [c["plotly_location"] for c in countries]
    map_values = [float(c["total_cases"]) for c in countries]

    return {
        "summary": summary,
        "trends": {
            "labels": trend_labels,
            "cases": cases,
            "recovered": recovered_t,
            "deaths": deaths_t,
        },
        "countries": countries,
        "vaccination": vaccination,
        "vaccination_pct_display": pct_fully,
        "news": news,
        "map": {"locations": map_locations, "values": map_values},
        "data_file": str(path),
        "data_updated": path.stat().st_mtime,
    }
