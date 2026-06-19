from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str = "airquality"
    postgres_password: str = "airquality_secret"
    postgres_db: str = "air_quality_santiago"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://localhost:8000"

    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8050

    log_level: str = "INFO"
    date_start: str = "2025-06-01"
    date_end: str = "2026-06-01"
    open_meteo_url: str = (
        "https://archive-api.open-meteo.com/v1/era5"
        "?latitude=-33.4521&longitude=-70.6536"
        "&start_date=2025-06-02&end_date=2026-06-02&wind_speed_unit=ms"
        "&daily=temperature_2m_max,temperature_2m_min,rain_sum,precipitation_sum,"
        "precipitation_hours,precipitation_probability_max,wind_speed_10m_max,"
        "wind_gusts_10m_max,weather_code&current=precipitation,rain"
    )
    station_name: str = "Santiago"
    etl_strict_validation: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def raw_data_dir(self) -> Path:
        return BASE_DIR / "data" / "raw"

    @property
    def processed_data_dir(self) -> Path:
        return BASE_DIR / "data" / "processed"

    @property
    def logs_dir(self) -> Path:
        return BASE_DIR / "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
