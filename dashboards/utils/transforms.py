from datetime import date

import pandas as pd

from dashboards.utils.constants import POLLUTANT_LABELS, UNIT_DISPLAY, WEATHER_VAR_MAP


def display_unit(unit: str) -> str:
    return UNIT_DISPLAY.get(unit, unit)


def display_pollutant(code: str) -> str:
    return POLLUTANT_LABELS.get(code, code)


def assign_season(d: date) -> str:
    month = d.month if isinstance(d, date) else pd.Timestamp(d).month
    if month in (12, 1, 2):
        return "Verano"
    if month in (3, 4, 5):
        return "Otoño"
    if month in (6, 7, 8):
        return "Invierno"
    return "Primavera"


def merge_pollution_weather(daily: list, weather: list) -> pd.DataFrame:
    if not daily or not weather:
        return pd.DataFrame()
    daily_df = pd.DataFrame(daily)
    weather_df = pd.DataFrame(weather)
    daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.date
    weather_df["date"] = pd.to_datetime(weather_df["date"]).dt.date
    wide = daily_df.pivot_table(
        index="date", columns="pollutant", values="avg_value", aggfunc="mean"
    ).reset_index()
    merged = wide.merge(weather_df, on="date", how="inner")
    return merged


def build_correlation_matrix(correlations: list) -> pd.DataFrame:
    if not correlations:
        return pd.DataFrame()
    from dashboards.utils.constants import CORRELATION_LABELS, CORRELATION_VARS

    corr_df = pd.DataFrame(correlations)
    pivot = corr_df.pivot(index="var_x", columns="var_y", values="correlation")
    available = [v for v in CORRELATION_VARS if v in pivot.index or v in pivot.columns]
    sub = pivot.reindex(index=available, columns=available)
    sub.index = [CORRELATION_LABELS.get(v, v) for v in sub.index]
    sub.columns = [CORRELATION_LABELS.get(v, v) for v in sub.columns]
    return sub


def get_correlation_value(correlations: list, var_x: str, var_y: str) -> float | None:
    for c in correlations:
        if (c["var_x"] == var_x and c["var_y"] == var_y) or (
            c["var_x"] == var_y and c["var_y"] == var_x
        ):
            return c["correlation"]
    return None
