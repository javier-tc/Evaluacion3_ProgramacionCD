from datetime import date, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


class PollutionRecord(BaseModel):
    measured_at: datetime
    pollutant: str
    value: float
    unit: str
    quality_status: str
    station_name: str

    model_config = {"from_attributes": True}


class DailyMetricResponse(BaseModel):
    date: date
    pollutant: str
    avg_value: float
    max_value: float
    unit: str

    model_config = {"from_attributes": True}


class MonthlyMetricResponse(BaseModel):
    year_month: str
    pollutant: str
    avg_value: float
    max_value: float
    unit: str

    model_config = {"from_attributes": True}


class WeatherRecord(BaseModel):
    date: date
    temp_max: float | None = None
    temp_min: float | None = None
    rain_sum: float | None = None
    precipitation_sum: float | None = None
    precip_hours: float | None = None
    precip_prob_max: float | None = None
    wind_speed_max: float | None = None
    wind_gusts_max: float | None = None
    weather_code: int | None = None

    model_config = {"from_attributes": True}


class CorrelationRecord(BaseModel):
    var_x: str
    var_y: str
    correlation: float
    method: str

    model_config = {"from_attributes": True}


class TrendRecord(BaseModel):
    pollutant: str
    slope: float
    intercept: float
    r_squared: float
    trend_direction: str


class TopPollutionDay(BaseModel):
    date: date
    pollutant: str
    value: float
    unit: str


class EtlStatusResponse(BaseModel):
    last_run: datetime | None
    status: str
    records_processed: int
    duration_seconds: float | None
    error_message: str | None = None


class DataQualityResponse(BaseModel):
    total_records: int
    valid_records: int
    preliminary_records: int
    non_validated_records: int
    missing_values_estimated: int
    duplicates_removed: int
    last_validation: datetime | None
    etl_last_run: datetime | None
    etl_records_processed: int
    etl_errors: int
    etl_duration_seconds: float | None


class PaginatedResponse(BaseModel):
    total: int
    items: list
