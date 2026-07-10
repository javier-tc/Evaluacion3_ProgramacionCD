import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from etl.models import DailyMetric, WeatherMeasurement
from models.config import (
    ALERT_TARGET_COLUMN,
    MP25_ALERT_THRESHOLDS,
    TARGET_COLUMN,
    WEATHER_FEATURES,
)


def classify_mp25_alert(value: float) -> str:
    if value <= MP25_ALERT_THRESHOLDS["normal"]:
        return "normal"
    if value <= MP25_ALERT_THRESHOLDS["moderado"]:
        return "moderado"
    return "alerta"


def build_feature_frame(daily_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    if daily_df.empty or weather_df.empty:
        return pd.DataFrame()

    daily = daily_df.copy()
    weather = weather_df.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    weather["date"] = pd.to_datetime(weather["date"])

    wide = (
        daily.pivot_table(
            index="date",
            columns="pollutant",
            values="avg_value",
            aggfunc="mean",
        )
        .reset_index()
        .rename(columns={"MP25": TARGET_COLUMN})
    )

    merged = wide.merge(weather, on="date", how="inner")
    if TARGET_COLUMN not in merged.columns:
        return pd.DataFrame()

    merged["month"] = merged["date"].dt.month
    merged["month_sin"] = np.sin(2 * np.pi * merged["month"] / 12)
    merged["month_cos"] = np.cos(2 * np.pi * merged["month"] / 12)
    merged[ALERT_TARGET_COLUMN] = merged[TARGET_COLUMN].apply(classify_mp25_alert)

    for column in WEATHER_FEATURES:
        if column not in merged.columns:
            merged[column] = 0.0
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
        if merged[column].isna().all():
            merged[column] = 0.0
        else:
            merged[column] = merged[column].fillna(merged[column].median())

    return merged.sort_values("date").reset_index(drop=True)


def fetch_training_frame_from_db(session: Session) -> pd.DataFrame:
    daily_rows = session.execute(
        select(
            DailyMetric.date,
            DailyMetric.pollutant,
            DailyMetric.avg_value,
            DailyMetric.max_value,
            DailyMetric.unit,
        )
    ).all()
    weather_rows = session.execute(
        select(
            WeatherMeasurement.date,
            WeatherMeasurement.temp_max,
            WeatherMeasurement.temp_min,
            WeatherMeasurement.rain_sum,
            WeatherMeasurement.precipitation_sum,
            WeatherMeasurement.precip_hours,
            WeatherMeasurement.precip_prob_max,
            WeatherMeasurement.wind_speed_max,
            WeatherMeasurement.wind_gusts_max,
            WeatherMeasurement.weather_code,
        )
    ).all()

    daily_df = pd.DataFrame(daily_rows)
    weather_df = pd.DataFrame(weather_rows)
    return build_feature_frame(daily_df, weather_df)


def split_features_target(frame: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series]:
    clean = frame.dropna(subset=[target]).copy()
    return clean[WEATHER_FEATURES], clean[target]

