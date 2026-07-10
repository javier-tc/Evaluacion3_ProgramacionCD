from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from etl.config import get_settings


class Base(DeclarativeBase):
    pass


class PollutionMeasurement(Base):
    __tablename__ = "pollution_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pollutant: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(20), nullable=False)
    station_name: Mapped[str] = mapped_column(String(50), nullable=False, default="Santiago")

    __table_args__ = (
        Index("ix_pollution_measured_at", "measured_at"),
        Index("ix_pollution_pollutant_measured", "pollutant", "measured_at"),
    )


class WeatherMeasurement(Base):
    __tablename__ = "weather_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    temp_max: Mapped[float | None] = mapped_column(Float)
    temp_min: Mapped[float | None] = mapped_column(Float)
    rain_sum: Mapped[float | None] = mapped_column(Float)
    precipitation_sum: Mapped[float | None] = mapped_column(Float)
    precip_hours: Mapped[float | None] = mapped_column(Float)
    precip_prob_max: Mapped[float | None] = mapped_column(Float)
    wind_speed_max: Mapped[float | None] = mapped_column(Float)
    wind_gusts_max: Mapped[float | None] = mapped_column(Float)
    weather_code: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (Index("ix_weather_date", "date"),)


class DailyMetric(Base):
    __tablename__ = "daily_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    pollutant: Mapped[str] = mapped_column(String(10), nullable=False)
    avg_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_daily_date_pollutant", "date", "pollutant", unique=True),
    )


class MonthlyMetric(Base):
    __tablename__ = "monthly_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)
    pollutant: Mapped[str] = mapped_column(String(10), nullable=False)
    avg_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_monthly_ym_pollutant", "year_month", "pollutant", unique=True),
    )


class CorrelationMatrix(Base):
    __tablename__ = "correlation_matrix"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    var_x: Mapped[str] = mapped_column(String(50), nullable=False)
    var_y: Mapped[str] = mapped_column(String(50), nullable=False)
    correlation: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False, default="pearson")
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class PollutionThreshold(Base):
    __tablename__ = "pollution_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pollutant: Mapped[str] = mapped_column(String(10), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_threshold_pollutant_level", "pollutant", "level", unique=True),
    )


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    model_name: Mapped[str] = mapped_column(String(80), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    artifact_path: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    trained_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_model_metric_task", "task_type", "model_name"),
    )


class EtlExecutionLog(Base):
    __tablename__ = "etl_execution_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(50), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory():
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
