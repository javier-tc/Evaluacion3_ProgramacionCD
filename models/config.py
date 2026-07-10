import os
from pathlib import Path

from etl.config import BASE_DIR

MODEL_RANDOM_STATE = int(os.getenv("ML_RANDOM_STATE", "42"))
TARGET_POLLUTANT = "MP25"
TARGET_COLUMN = "mp25_avg"
ALERT_TARGET_COLUMN = "mp25_alert_level"
ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "models"

WEATHER_FEATURES = [
    "temp_max",
    "temp_min",
    "rain_sum",
    "precipitation_sum",
    "precip_hours",
    "precip_prob_max",
    "wind_speed_max",
    "wind_gusts_max",
    "weather_code",
    "month_sin",
    "month_cos",
]

MP25_ALERT_THRESHOLDS = {
    "normal": float(os.getenv("MP25_NORMAL_THRESHOLD", "25")),
    "moderado": float(os.getenv("MP25_MODERATE_THRESHOLD", "50")),
}


def ensure_artifact_dir(path: Path = ARTIFACT_DIR) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

