import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.responses import (
    ModelMetricResponse,
    RegressionPredictionRequest,
    RegressionPredictionResponse,
)
from api.services.queries import get_model_metrics
from models.config import TARGET_COLUMN, WEATHER_FEATURES
from models.registry import load_latest_model

router = APIRouter(prefix="/analytics/ml", tags=["machine-learning"])


@router.get("/metrics", response_model=list[ModelMetricResponse])
def metrics(db: Session = Depends(get_db)):
    return get_model_metrics(db)


@router.post("/predict/regression", response_model=RegressionPredictionResponse)
def predict_regression(payload: RegressionPredictionRequest):
    model, metadata = load_latest_model("regression")
    if model is None or metadata is None:
        raise HTTPException(status_code=404, detail="no hay modelo de regresion entrenado")

    month_sin = np.sin(2 * np.pi * payload.month / 12)
    month_cos = np.cos(2 * np.pi * payload.month / 12)
    row = {
        "temp_max": payload.temp_max,
        "temp_min": payload.temp_min,
        "rain_sum": payload.rain_sum,
        "precipitation_sum": payload.precipitation_sum,
        "precip_hours": payload.precip_hours,
        "precip_prob_max": payload.precip_prob_max,
        "wind_speed_max": payload.wind_speed_max,
        "wind_gusts_max": payload.wind_gusts_max,
        "weather_code": payload.weather_code or 0,
        "month_sin": month_sin,
        "month_cos": month_cos,
    }
    prediction = model.predict(pd.DataFrame([row], columns=WEATHER_FEATURES))[0]
    return RegressionPredictionResponse(
        model_name=metadata["model_name"],
        target=TARGET_COLUMN,
        predicted_value=float(prediction),
    )

