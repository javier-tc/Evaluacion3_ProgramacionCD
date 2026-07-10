import pandas as pd

from models.config import ALERT_TARGET_COLUMN, TARGET_COLUMN
from models.features import build_feature_frame
from models.train_classification import train_classification_models
from models.train_regression import train_regression_models


def _daily_weather_frames():
    dates = pd.date_range("2025-06-01", periods=12, freq="D")
    mp25_values = [12, 18, 22, 25, 31, 38, 44, 50, 55, 62, 70, 78]
    daily = pd.DataFrame({
        "date": dates,
        "pollutant": ["MP25"] * len(dates),
        "avg_value": mp25_values,
        "max_value": mp25_values,
        "unit": ["ug/m3"] * len(dates),
    })
    weather = pd.DataFrame({
        "date": dates,
        "temp_max": [18, 19, 20, 21, 22, 23, 20, 19, 18, 17, 16, 15],
        "temp_min": [8, 9, 10, 11, 12, 13, 12, 11, 10, 9, 8, 7],
        "rain_sum": [0, 0, 1, 0, 2, 0, 3, 0, 1, 0, 0, 2],
        "precipitation_sum": [0, 0, 1, 0, 2, 0, 3, 0, 1, 0, 0, 2],
        "precip_hours": [0, 0, 2, 0, 3, 0, 4, 0, 2, 0, 0, 3],
        "precip_prob_max": [5, 10, 50, 10, 70, 20, 80, 15, 55, 10, 5, 60],
        "wind_speed_max": [6, 7, 5, 8, 4, 6, 3, 7, 5, 6, 8, 4],
        "wind_gusts_max": [10, 11, 9, 12, 8, 10, 7, 11, 9, 10, 12, 8],
        "weather_code": [0, 0, 61, 0, 63, 1, 61, 0, 51, 0, 0, 63],
    })
    return daily, weather


def test_build_feature_frame_creates_targets():
    daily, weather = _daily_weather_frames()
    frame = build_feature_frame(daily, weather)
    assert TARGET_COLUMN in frame.columns
    assert ALERT_TARGET_COLUMN in frame.columns
    assert set(frame[ALERT_TARGET_COLUMN]) == {"normal", "moderado", "alerta"}


def test_train_regression_models_returns_metrics():
    daily, weather = _daily_weather_frames()
    frame = build_feature_frame(daily, weather)
    results = train_regression_models(frame)
    assert len(results) == 3
    assert "mae" in results[0]["metrics"]


def test_train_classification_models_returns_metrics():
    daily, weather = _daily_weather_frames()
    frame = build_feature_frame(daily, weather)
    results = train_classification_models(frame)
    assert len(results) == 3
    assert "f1_macro" in results[0]["metrics"]

