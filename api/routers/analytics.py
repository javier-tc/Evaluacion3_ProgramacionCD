from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.responses import (
    CorrelationRecord,
    DataQualityResponse,
    EtlStatusResponse,
    TopPollutionDay,
    TrendRecord,
)
from api.services.queries import (
    get_annual_averages,
    get_correlations,
    get_data_quality,
    get_etl_status,
    get_top_pollution_days,
    get_trends,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/correlation", response_model=list[CorrelationRecord])
def correlations(db: Session = Depends(get_db)):
    return get_correlations(db)


@router.get("/trends", response_model=list[TrendRecord])
def trends(db: Session = Depends(get_db)):
    return get_trends(db)


@router.get("/top-pollution-days", response_model=list[TopPollutionDay])
def top_pollution_days(
    pollutant: str | None = Query(None),
    top_n: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_top_pollution_days(db, pollutant, top_n)


@router.get("/annual-averages")
def annual_averages(db: Session = Depends(get_db)):
    return get_annual_averages(db)


@router.get("/etl-status", response_model=EtlStatusResponse)
def etl_status(db: Session = Depends(get_db)):
    return get_etl_status(db)


@router.get("/data-quality", response_model=DataQualityResponse)
def data_quality(db: Session = Depends(get_db)):
    return get_data_quality(db)
