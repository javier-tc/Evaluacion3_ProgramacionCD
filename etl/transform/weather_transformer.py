import pandas as pd
from loguru import logger

from etl.config import get_settings


def transform_weather(weather_df: pd.DataFrame) -> pd.DataFrame:
    settings = get_settings()
    start = pd.Timestamp(settings.date_start).date()
    end = pd.Timestamp(settings.date_end).date()

    df = weather_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"]).dt.date
    else:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    df = df[(df["date"] >= start) & (df["date"] <= end)]
    df = df.drop_duplicates(subset=["date"], keep="first")

    numeric_cols = [
        "temp_max", "temp_min", "rain_sum", "precipitation_sum",
        "precip_hours", "precip_prob_max", "wind_speed_max", "wind_gusts_max",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "weather_code" in df.columns:
        df["weather_code"] = pd.to_numeric(df["weather_code"], errors="coerce").astype("Int64")

    logger.info(f"transformacion clima: {len(df)} registros")
    return df
