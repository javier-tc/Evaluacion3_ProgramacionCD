import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.models import Base


@pytest.fixture
def sample_pollution_df():
    return pd.DataFrame({
        "measured_at": [datetime(2025, 6, 11), datetime(2025, 6, 12)],
        "pollutant": ["MP25", "MP25"],
        "value": [34.0, 18.0],
        "unit": ["ug/m3", "ug/m3"],
        "quality_status": ["validated", "validated"],
        "station_name": ["Santiago", "Santiago"],
    })


@pytest.fixture
def sample_weather_df():
    return pd.DataFrame({
        "date": [pd.Timestamp("2025-06-11").date(), pd.Timestamp("2025-06-12").date()],
        "temp_max": [20.0, 22.0],
        "temp_min": [10.0, 12.0],
        "rain_sum": [0.0, 1.5],
        "precipitation_sum": [0.0, 1.5],
        "precip_hours": [0.0, 2.0],
        "precip_prob_max": [10.0, 50.0],
        "wind_speed_max": [5.0, 8.0],
        "wind_gusts_max": [10.0, 15.0],
        "weather_code": [0, 61],
    })


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(sqlite_engine):
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def raw_csv_dir():
    return Path(__file__).resolve().parent.parent / "data" / "raw"
