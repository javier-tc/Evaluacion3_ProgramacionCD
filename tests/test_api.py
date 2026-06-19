from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_db
from api.main import app
from etl.models import DailyMetric, PollutionMeasurement


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@patch("api.routers.health.check_db_connection", return_value=True)
def test_health(mock_check, client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("api.routers.pollution.get_pollution")
def test_pollution_endpoint(mock_get, client):
    mock_get.return_value = [
        PollutionMeasurement(
            id=1,
            measured_at=datetime(2025, 6, 11),
            pollutant="MP25",
            value=34.0,
            unit="ug/m3",
            quality_status="validated",
            station_name="Santiago",
        )
    ]
    response = client.get("/pollution?pollutant=MP25")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("api.routers.pollution.get_daily_metrics")
def test_pollution_daily(mock_get, client):
    mock_get.return_value = [
        DailyMetric(
            id=1, date=datetime(2025, 6, 11).date(),
            pollutant="MP25", avg_value=34.0, max_value=34.0, unit="ug/m3",
        )
    ]
    response = client.get("/pollution/daily")
    assert response.status_code == 200


@patch("api.routers.weather.get_weather")
def test_weather(mock_get, client):
    mock_get.return_value = []
    response = client.get("/weather")
    assert response.status_code == 200


@patch("api.routers.pollution.get_monthly_metrics")
def test_pollution_monthly(mock_get, client):
    mock_get.return_value = []
    response = client.get("/pollution/monthly")
    assert response.status_code == 200


@patch("api.routers.analytics.get_correlations")
def test_correlation(mock_get, client):
    mock_get.return_value = []
    response = client.get("/analytics/correlation")
    assert response.status_code == 200


@patch("api.routers.analytics.get_trends")
def test_trends(mock_get, client):
    mock_get.return_value = []
    response = client.get("/analytics/trends")
    assert response.status_code == 200


@patch("api.routers.analytics.get_top_pollution_days")
def test_top_days(mock_get, client):
    mock_get.return_value = []
    response = client.get("/analytics/top-pollution-days?top_n=5")
    assert response.status_code == 200


@patch("api.routers.analytics.get_annual_averages")
def test_annual_averages(mock_get, client):
    mock_get.return_value = [
        {"pollutant": "MP25", "year": 2025, "avg_value": 28.5, "unit": "ug/m3"}
    ]
    response = client.get("/analytics/annual-averages")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("api.routers.analytics.get_etl_status")
def test_etl_status(mock_get, client):
    mock_get.return_value = {
        "last_run": None,
        "status": "no_runs",
        "records_processed": 0,
        "duration_seconds": None,
        "error_message": None,
    }
    response = client.get("/analytics/etl-status")
    assert response.status_code == 200


@patch("api.routers.analytics.get_data_quality")
def test_data_quality(mock_get, client):
    mock_get.return_value = {
        "total_records": 100,
        "valid_records": 80,
        "preliminary_records": 15,
        "non_validated_records": 5,
        "missing_values_estimated": 3,
        "duplicates_removed": 2,
        "last_validation": None,
        "etl_last_run": None,
        "etl_records_processed": 100,
        "etl_errors": 0,
        "etl_duration_seconds": 12.5,
    }
    response = client.get("/analytics/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 100
    assert data["valid_records"] == 80
