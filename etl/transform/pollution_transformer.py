import numpy as np
import pandas as pd
from loguru import logger

from etl.config import get_settings


def _parse_value(val) -> float | None:
    if pd.isna(val) or val == "" or val is None:
        return None
    if isinstance(val, str):
        val = val.replace(",", ".")
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _coalesce_value(row) -> tuple[float | None, str | None]:
    for col, status in [
        ("valor_validado", "validated"),
        ("valor_preliminar", "preliminary"),
        ("valor_no_validado", "non_validated"),
    ]:
        v = _parse_value(row[col])
        if v is not None:
            return v, status
    return None, None


def _to_numeric_series(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.replace(",", ".", regex=False)
    return pd.to_numeric(normalized, errors="coerce")


def _coalesce_columns(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    columns = ["valor_validado", "valor_preliminar", "valor_no_validado"]
    statuses = ["validated", "preliminary", "non_validated"]
    numeric = pd.concat([_to_numeric_series(df[col]) for col in columns], axis=1)
    numeric.columns = columns
    value = numeric.bfill(axis=1).iloc[:, 0]
    status = np.select(
        [numeric[col].notna() for col in columns],
        statuses,
        default=None,
    )
    return value, pd.Series(status, index=df.index, dtype="object")


def _build_timestamp(fecha: int | str, hora: int | str) -> pd.Timestamp:
    fecha_str = str(int(fecha)).zfill(6)
    hora_str = str(int(hora)).zfill(4)
    dt_str = f"20{fecha_str} {hora_str[:2]}:{hora_str[2:]}"
    return pd.to_datetime(dt_str, format="%Y%m%d %H:%M")


def _build_timestamps(df: pd.DataFrame) -> pd.Series:
    fecha = df["fecha"].astype("int64").astype("string").str.zfill(6)
    hora = df["hora"].astype("int64").astype("string").str.zfill(4)
    dt_str = "20" + fecha + " " + hora.str[:2] + ":" + hora.str[2:]
    return pd.to_datetime(dt_str, format="%Y%m%d %H:%M", errors="coerce")


def transform_pollution(pollution_dfs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    start = pd.Timestamp(settings.date_start)
    end = pd.Timestamp(settings.date_end)

    frames = []
    for pollutant, df in pollution_dfs.items():
        df = df.copy()
        df["value"], df["quality_status"] = _coalesce_columns(df)
        df["measured_at"] = _build_timestamps(df)
        df["station_name"] = settings.station_name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["value"])
    combined = combined[combined["value"] >= 0]
    combined = combined[
        (combined["measured_at"] >= start) & (combined["measured_at"] <= end)
    ]
    combined = combined.drop_duplicates(
        subset=["measured_at", "pollutant"], keep="first"
    )

    result = combined[
        ["measured_at", "pollutant", "value", "unit", "quality_status", "station_name"]
    ].copy()

    daily = (
        result.groupby([result["measured_at"].dt.date, "pollutant", "unit"])
        .agg(avg_value=("value", "mean"), max_value=("value", "max"))
        .reset_index()
        .rename(columns={"measured_at": "date"})
    )
    daily["date"] = pd.to_datetime(daily["date"]).dt.date

    monthly = (
        result.assign(year_month=result["measured_at"].dt.strftime("%Y-%m"))
        .groupby(["year_month", "pollutant", "unit"])
        .agg(avg_value=("value", "mean"), max_value=("value", "max"))
        .reset_index()
    )

    logger.info(
        f"transformacion contaminacion: {len(result)} registros, "
        f"{len(daily)} diarios, {len(monthly)} mensuales"
    )
    return result, daily, monthly


def compute_correlations(
    pollution_df: pd.DataFrame, weather_df: pd.DataFrame
) -> pd.DataFrame:
    poll_daily_wide = (
        pollution_df.assign(date=pollution_df["measured_at"].dt.date)
        .pivot_table(index="date", columns="pollutant", values="value", aggfunc="mean")
        .reset_index()
    )
    poll_daily_long = poll_daily_wide.melt(
        id_vars="date",
        var_name="pollutant",
        value_name="daily_avg",
    ).dropna()
    poll_daily = (
        poll_daily_long.pivot_table(
            index="date",
            columns="pollutant",
            values="daily_avg",
            aggfunc="mean",
        )
        .reset_index()
    )
    merged = poll_daily.merge(weather_df, on="date", how="inner")
    numeric = merged.select_dtypes(include="number")
    corr = numeric.corr(method="pearson")

    records = []
    for var_x in corr.columns:
        for var_y in corr.columns:
            if var_x <= var_y:
                records.append(
                    {
                        "var_x": var_x,
                        "var_y": var_y,
                        "correlation": corr.loc[var_x, var_y],
                        "method": "pearson",
                    }
                )
    return pd.DataFrame(records)
