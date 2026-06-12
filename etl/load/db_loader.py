from datetime import datetime

import pandas as pd
from loguru import logger
from sqlalchemy import delete

from etl.models import (
    CorrelationMatrix,
    DailyMetric,
    EtlExecutionLog,
    MonthlyMetric,
    PollutionMeasurement,
    WeatherMeasurement,
    get_engine,
    get_session_factory,
)

CHUNK_SIZE = 1000


def _log_stage(session, run_id: str, stage: str, status: str,
               records: int = 0, error: str | None = None,
               started: datetime | None = None, duration: float | None = None):
    log = EtlExecutionLog(
        run_id=run_id,
        stage=stage,
        status=status,
        records_count=records,
        error_message=error,
        duration_seconds=duration,
        started_at=started or datetime.now(),
        finished_at=datetime.now() if status != "running" else None,
    )
    session.add(log)
    session.flush()


def load_all_data(
    pollution_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    correlation_df: pd.DataFrame,
    run_id: str,
) -> int:
    engine = get_engine()
    Session = get_session_factory()
    total_records = 0
    started = datetime.now()

    with Session() as session:
        try:
            _log_stage(session, run_id, "load", "running", started=started)

            session.execute(delete(PollutionMeasurement))
            session.execute(delete(WeatherMeasurement))
            session.execute(delete(DailyMetric))
            session.execute(delete(MonthlyMetric))
            session.execute(delete(CorrelationMatrix))

            for _, row in pollution_df.iterrows():
                session.add(PollutionMeasurement(
                    measured_at=row["measured_at"],
                    pollutant=row["pollutant"],
                    value=float(row["value"]),
                    unit=row["unit"],
                    quality_status=row["quality_status"],
                    station_name=row["station_name"],
                ))
            total_records += len(pollution_df)

            for _, row in weather_df.iterrows():
                wc = row.get("weather_code")
                session.add(WeatherMeasurement(
                    date=row["date"],
                    temp_max=row.get("temp_max"),
                    temp_min=row.get("temp_min"),
                    rain_sum=row.get("rain_sum"),
                    precipitation_sum=row.get("precipitation_sum"),
                    precip_hours=row.get("precip_hours"),
                    precip_prob_max=row.get("precip_prob_max"),
                    wind_speed_max=row.get("wind_speed_max"),
                    wind_gusts_max=row.get("wind_gusts_max"),
                    weather_code=int(wc) if pd.notna(wc) else None,
                ))
            total_records += len(weather_df)

            for _, row in daily_df.iterrows():
                session.add(DailyMetric(
                    date=row["date"],
                    pollutant=row["pollutant"],
                    avg_value=float(row["avg_value"]),
                    max_value=float(row["max_value"]),
                    unit=row["unit"],
                ))

            for _, row in monthly_df.iterrows():
                session.add(MonthlyMetric(
                    year_month=row["year_month"],
                    pollutant=row["pollutant"],
                    avg_value=float(row["avg_value"]),
                    max_value=float(row["max_value"]),
                    unit=row["unit"],
                ))

            computed_at = datetime.now()
            for _, row in correlation_df.iterrows():
                if pd.notna(row["correlation"]):
                    session.add(CorrelationMatrix(
                        var_x=row["var_x"],
                        var_y=row["var_y"],
                        correlation=float(row["correlation"]),
                        method=row.get("method", "pearson"),
                        computed_at=computed_at,
                    ))

            duration = (datetime.now() - started).total_seconds()
            _log_stage(session, run_id, "load", "success", total_records,
                       started=started, duration=duration)
            session.commit()
            logger.info(f"carga completada: {total_records} registros en {duration:.2f}s")

        except Exception as exc:
            session.rollback()
            _log_stage(session, run_id, "load", "failed", error=str(exc), started=started)
            session.commit()
            logger.error(f"error en carga - rollback ejecutado: {exc}")
            raise

    return total_records
