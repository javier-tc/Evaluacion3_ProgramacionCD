from datetime import date, datetime

import numpy as np
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from etl.models import (
    CorrelationMatrix,
    DailyMetric,
    EtlExecutionLog,
    MonthlyMetric,
    PollutionMeasurement,
    WeatherMeasurement,
)


def check_db_connection(db: Session) -> bool:
    try:
        db.execute(select(1))
        return True
    except Exception:
        return False


def get_pollution(
    db: Session,
    pollutant: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 1000,
) -> list[PollutionMeasurement]:
    q = select(PollutionMeasurement)
    if pollutant:
        q = q.where(PollutionMeasurement.pollutant == pollutant)
    if start_date:
        q = q.where(PollutionMeasurement.measured_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        q = q.where(PollutionMeasurement.measured_at <= datetime.combine(end_date, datetime.max.time()))
    q = q.order_by(PollutionMeasurement.measured_at).limit(limit)
    return list(db.scalars(q).all())


def get_daily_metrics(
    db: Session,
    pollutant: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[DailyMetric]:
    q = select(DailyMetric)
    if pollutant:
        q = q.where(DailyMetric.pollutant == pollutant)
    if start_date:
        q = q.where(DailyMetric.date >= start_date)
    if end_date:
        q = q.where(DailyMetric.date <= end_date)
    q = q.order_by(DailyMetric.date)
    return list(db.scalars(q).all())


def get_monthly_metrics(
    db: Session,
    pollutant: str | None = None,
) -> list[MonthlyMetric]:
    q = select(MonthlyMetric)
    if pollutant:
        q = q.where(MonthlyMetric.pollutant == pollutant)
    q = q.order_by(MonthlyMetric.year_month)
    return list(db.scalars(q).all())


def get_weather(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[WeatherMeasurement]:
    q = select(WeatherMeasurement)
    if start_date:
        q = q.where(WeatherMeasurement.date >= start_date)
    if end_date:
        q = q.where(WeatherMeasurement.date <= end_date)
    q = q.order_by(WeatherMeasurement.date)
    return list(db.scalars(q).all())


def get_correlations(db: Session) -> list[CorrelationMatrix]:
    return list(db.scalars(select(CorrelationMatrix)).all())


def get_trends(db: Session) -> list[dict]:
    daily = get_daily_metrics(db)
    pollutants = {d.pollutant for d in daily}
    trends = []
    for pol in pollutants:
        records = sorted(
            [(d.date, d.avg_value) for d in daily if d.pollutant == pol],
            key=lambda x: x[0],
        )
        if len(records) < 2:
            continue
        x = np.arange(len(records))
        y = np.array([r[1] for r in records])
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs[0], coeffs[1]
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        trends.append({
            "pollutant": pol,
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "trend_direction": "increasing" if slope > 0 else "decreasing",
        })
    return trends


def get_top_pollution_days(
    db: Session,
    pollutant: str | None = None,
    top_n: int = 10,
) -> list[dict]:
    q = select(DailyMetric)
    if pollutant:
        q = q.where(DailyMetric.pollutant == pollutant)
    q = q.order_by(desc(DailyMetric.max_value)).limit(top_n)
    results = db.scalars(q).all()
    return [
        {"date": r.date, "pollutant": r.pollutant, "value": r.max_value, "unit": r.unit}
        for r in results
    ]


def get_etl_status(db: Session) -> dict:
    q = (
        select(EtlExecutionLog)
        .where(EtlExecutionLog.stage == "pipeline")
        .order_by(desc(EtlExecutionLog.started_at))
        .limit(1)
    )
    last = db.scalars(q).first()
    if not last:
        return {
            "last_run": None,
            "status": "no_runs",
            "records_processed": 0,
            "duration_seconds": None,
            "error_message": None,
        }
    return {
        "last_run": last.started_at,
        "status": last.status,
        "records_processed": last.records_count,
        "duration_seconds": last.duration_seconds,
        "error_message": last.error_message,
    }


def get_annual_averages(db: Session) -> list[dict]:
    q = (
        select(
            DailyMetric.pollutant,
            DailyMetric.unit,
            func.avg(DailyMetric.avg_value).label("annual_avg"),
        )
        .group_by(DailyMetric.pollutant, DailyMetric.unit)
    )
    return [
        {"pollutant": r.pollutant, "unit": r.unit, "annual_avg": float(r.annual_avg)}
        for r in db.execute(q).all()
    ]
