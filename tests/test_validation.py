from datetime import datetime

import pandas as pd
import pytest
from pydantic import ValidationError

from etl.validation.schemas import PollutionRecord, WeatherRecord
from etl.validation.validator import validate_datasets


def test_pollution_record_valid():
    record = PollutionRecord(
        measured_at=datetime(2025, 6, 11),
        pollutant="MP25",
        value=34.0,
        unit="ug/m3",
        quality_status="validated",
    )
    assert record.pollutant == "MP25"


def test_pollution_record_negative_rejected():
    with pytest.raises(ValidationError):
        PollutionRecord(
            measured_at=datetime(2025, 6, 11),
            pollutant="MP25",
            value=-1.0,
            unit="ug/m3",
            quality_status="validated",
        )


def test_weather_record_temp_validation():
    with pytest.raises(ValidationError):
        WeatherRecord(
            date=datetime(2025, 6, 11).date(),
            temp_max=10.0,
            temp_min=20.0,
        )


def test_validate_datasets(sample_pollution_df, sample_weather_df, tmp_path):
    report = validate_datasets(sample_pollution_df, sample_weather_df, tmp_path)
    assert "pollution" in report
    assert "weather" in report
    assert report["pollution"]["pydantic_valid"] == 2
