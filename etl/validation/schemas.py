from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class PollutantEnum(str, Enum):
    CO = "CO"
    MP10 = "MP10"
    MP25 = "MP25"
    NO2 = "NO2"
    O3 = "O3"


class QualityStatus(str, Enum):
    VALIDATED = "validated"
    PRELIMINARY = "preliminary"
    NON_VALIDATED = "non_validated"


class PollutionRecord(BaseModel):
    measured_at: datetime
    pollutant: PollutantEnum
    value: float = Field(ge=0)
    unit: str
    quality_status: QualityStatus
    station_name: str = "Santiago"


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

    @model_validator(mode="after")
    def check_temperatures(self):
        if (
            self.temp_max is not None
            and self.temp_min is not None
            and self.temp_min > self.temp_max
        ):
            raise ValueError("temp_min no puede ser mayor que temp_max")
        return self

    @field_validator("rain_sum", "precipitation_sum", "precip_hours", "precip_prob_max",
                     "wind_speed_max", "wind_gusts_max", mode="before")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("valor no puede ser negativo")
        return v
