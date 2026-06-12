import pandas as pd

from etl.load import db_loader
from etl.models import PollutionMeasurement


def test_load_all_data_sqlite(sqlite_engine, sample_pollution_df, sample_weather_df):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=sqlite_engine)
    original_engine = db_loader.get_engine
    original_session = db_loader.get_session_factory
    db_loader.get_engine = lambda: sqlite_engine
    db_loader.get_session_factory = lambda: Session

    daily = pd.DataFrame({
        "date": [sample_pollution_df["measured_at"].iloc[0].date()],
        "pollutant": ["MP25"],
        "avg_value": [34.0],
        "max_value": [34.0],
        "unit": ["ug/m3"],
    })
    monthly = pd.DataFrame({
        "year_month": ["2025-06"],
        "pollutant": ["MP25"],
        "avg_value": [26.0],
        "max_value": [34.0],
        "unit": ["ug/m3"],
    })
    corr = pd.DataFrame({
        "var_x": ["MP25"],
        "var_y": ["temp_max"],
        "correlation": [0.5],
        "method": ["pearson"],
    })

    try:
        total = db_loader.load_all_data(
            sample_pollution_df, sample_weather_df, daily, monthly, corr, "test01"
        )
        assert total > 0
        with Session() as session:
            assert session.query(PollutionMeasurement).count() == 2
    finally:
        db_loader.get_engine = original_engine
        db_loader.get_session_factory = original_session
