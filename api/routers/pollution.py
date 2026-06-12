from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.responses import DailyMetricResponse, MonthlyMetricResponse, PollutionRecord
from api.services.queries import get_daily_metrics, get_monthly_metrics, get_pollution

router = APIRouter(prefix="/pollution", tags=["pollution"])

POLLUTANTS = ["CO", "MP10", "MP25", "NO2", "O3"]


@router.get("", response_model=list[PollutionRecord])
def list_pollution(
    pollutant: str | None = Query(None, description="filtro por contaminante"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    if pollutant and pollutant not in POLLUTANTS:
        pollutant = None
    return get_pollution(db, pollutant, start_date, end_date, limit)


@router.get("/daily", response_model=list[DailyMetricResponse])
def list_daily(
    pollutant: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_daily_metrics(db, pollutant, start_date, end_date)


@router.get("/monthly", response_model=list[MonthlyMetricResponse])
def list_monthly(
    pollutant: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_monthly_metrics(db, pollutant)
