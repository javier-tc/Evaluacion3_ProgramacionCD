import pandas as pd
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from etl.models import PollutionThreshold, get_session_factory

DEFAULT_THRESHOLDS = [
    {"pollutant": "MP25", "level": "normal", "threshold_value": 25.0, "unit": "ug/m3"},
    {"pollutant": "MP25", "level": "moderado", "threshold_value": 50.0, "unit": "ug/m3"},
    {"pollutant": "MP10", "level": "normal", "threshold_value": 50.0, "unit": "ug/m3"},
    {"pollutant": "MP10", "level": "moderado", "threshold_value": 150.0, "unit": "ug/m3"},
]


def seed_reference_thresholds(session: Session) -> None:
    existing = {
        (row.pollutant, row.level)
        for row in session.scalars(select(PollutionThreshold)).all()
    }
    for threshold in DEFAULT_THRESHOLDS:
        key = (threshold["pollutant"], threshold["level"])
        if key not in existing:
            session.add(PollutionThreshold(
                pollutant=threshold["pollutant"],
                level=threshold["level"],
                threshold_value=threshold["threshold_value"],
                unit=threshold["unit"],
                source="referencia operacional proyecto",
            ))
    session.commit()


def extract_pollution_thresholds() -> pd.DataFrame:
    Session = get_session_factory()
    with Session() as session:
        seed_reference_thresholds(session)
        rows = session.scalars(select(PollutionThreshold)).all()
        records = [{
            "pollutant": row.pollutant,
            "level": row.level,
            "threshold_value": row.threshold_value,
            "unit": row.unit,
            "source": row.source,
        } for row in rows]
    logger.info(f"umbrales extraidos desde bbdd: {len(records)} registros")
    return pd.DataFrame(records)


def enrich_daily_metrics_with_thresholds(
    daily_df: pd.DataFrame,
    thresholds_df: pd.DataFrame,
) -> pd.DataFrame:
    if daily_df.empty or thresholds_df.empty:
        return daily_df.copy()

    normal = thresholds_df[thresholds_df["level"] == "normal"][
        ["pollutant", "threshold_value"]
    ].rename(columns={"threshold_value": "normal_threshold"})
    moderate = thresholds_df[thresholds_df["level"] == "moderado"][
        ["pollutant", "threshold_value"]
    ].rename(columns={"threshold_value": "moderate_threshold"})

    enriched = daily_df.merge(normal, on="pollutant", how="left")
    enriched = enriched.merge(moderate, on="pollutant", how="left")
    enriched["threshold_level"] = "sin_umbral"
    has_threshold = enriched["normal_threshold"].notna()
    enriched.loc[has_threshold, "threshold_level"] = "normal"
    enriched.loc[
        has_threshold & (enriched["avg_value"] > enriched["normal_threshold"]),
        "threshold_level",
    ] = "moderado"
    enriched.loc[
        enriched["moderate_threshold"].notna()
        & (enriched["avg_value"] > enriched["moderate_threshold"]),
        "threshold_level",
    ] = "alerta"
    return enriched

