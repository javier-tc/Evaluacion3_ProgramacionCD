import json
from pathlib import Path

import pandas as pd
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from etl.config import get_settings

REQUIRED_DAILY_KEYS = [
    "time",
    "temperature_2m_max",
    "temperature_2m_min",
    "rain_sum",
    "precipitation_sum",
    "precipitation_hours",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "weather_code",
]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_weather_api(url: str) -> dict:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    if response.status_code != 200:
        raise requests.HTTPError(f"respuesta http inesperada: {response.status_code}")
    return response.json()


def _validate_weather_response(data: dict) -> None:
    if "daily" not in data:
        raise ValueError("respuesta open-meteo sin seccion daily")
    daily = data["daily"]
    missing = [k for k in REQUIRED_DAILY_KEYS if k not in daily]
    if missing:
        raise ValueError(f"campos faltantes en respuesta: {missing}")


def extract_weather(save_path: Path | None = None) -> pd.DataFrame:
    settings = get_settings()
    logger.info("extrayendo datos meteorologicos de open-meteo")
    data = _fetch_weather_api(settings.open_meteo_url)
    _validate_weather_response(data)

    daily = data["daily"]
    df = pd.DataFrame(daily)
    df = df.rename(
        columns={
            "time": "date",
            "temperature_2m_max": "temp_max",
            "temperature_2m_min": "temp_min",
            "rain_sum": "rain_sum",
            "precipitation_sum": "precipitation_sum",
            "precipitation_hours": "precip_hours",
            "precipitation_probability_max": "precip_prob_max",
            "wind_speed_10m_max": "wind_speed_max",
            "wind_gusts_10m_max": "wind_gusts_max",
            "weather_code": "weather_code",
        }
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"snapshot api guardado en {save_path}")

    logger.info(f"extraidos {len(df)} registros meteorologicos")
    return df
