import os
from datetime import date

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 30.0

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToAdd": ["toImage"],
    "toImageButtonOptions": {"format": "png", "filename": "grafico_calidad_aire"},
}


def _get(path: str, params: dict | None = None) -> list | dict:
    try:
        with httpx.Client(base_url=API_URL, timeout=TIMEOUT) as client:
            response = client.get(path, params=params or {})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return [] if path != "/health" else {"status": "error", "database": "disconnected"}


def get_health() -> dict:
    return _get("/health")


def get_pollution(pollutant: str | None = None, start: date | None = None, end: date | None = None) -> list:
    params = {}
    if pollutant:
        params["pollutant"] = pollutant
    if start:
        params["start_date"] = start.isoformat()
    if end:
        params["end_date"] = end.isoformat()
    return _get("/pollution", params)


def get_daily(pollutant: str | None = None, start: date | None = None, end: date | None = None) -> list:
    params = {}
    if pollutant:
        params["pollutant"] = pollutant
    if start:
        params["start_date"] = start.isoformat()
    if end:
        params["end_date"] = end.isoformat()
    return _get("/pollution/daily", params)


def get_monthly(pollutant: str | None = None) -> list:
    params = {}
    if pollutant:
        params["pollutant"] = pollutant
    return _get("/pollution/monthly", params)


def get_weather(start: date | None = None, end: date | None = None) -> list:
    params = {}
    if start:
        params["start_date"] = start.isoformat()
    if end:
        params["end_date"] = end.isoformat()
    return _get("/weather", params)


def get_correlations() -> list:
    return _get("/analytics/correlation")


def get_trends() -> list:
    return _get("/analytics/trends")


def get_top_days(pollutant: str | None = None, top_n: int = 10) -> list:
    params = {"top_n": top_n}
    if pollutant:
        params["pollutant"] = pollutant
    return _get("/analytics/top-pollution-days", params)


def get_annual_averages() -> list:
    return _get("/analytics/annual-averages")


def get_etl_status() -> dict:
    return _get("/analytics/etl-status")


def get_data_quality() -> dict:
    result = _get("/analytics/data-quality")
    return result if isinstance(result, dict) else {}


def get_model_metrics() -> list:
    result = _get("/analytics/ml/metrics")
    return result if isinstance(result, list) else []
