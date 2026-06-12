from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.responses import WeatherRecord
from api.services.queries import get_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=list[WeatherRecord])
def list_weather(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_weather(db, start_date, end_date)
