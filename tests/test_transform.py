from datetime import datetime

import pandas as pd

from etl.transform.pollution_transformer import _coalesce_value, transform_pollution
from etl.transform.weather_transformer import transform_weather


def test_coalesce_validated_first():
    row = pd.Series({
        "valor_validado": 10,
        "valor_preliminar": 20,
        "valor_no_validado": 30,
    })
    val, status = _coalesce_value(row)
    assert val == 10
    assert status == "validated"


def test_coalesce_preliminary():
    row = pd.Series({
        "valor_validado": "",
        "valor_preliminar": "25",
        "valor_no_validado": 30,
    })
    val, status = _coalesce_value(row)
    assert val == 25
    assert status == "preliminary"


def test_transform_pollution_filters_dates(raw_csv_dir):
    from etl.extract.csv_extractor import extract_all_csv
    pollution_dfs = extract_all_csv(raw_csv_dir)
    result, daily, monthly = transform_pollution(pollution_dfs)
    assert len(result) > 0
    assert result["value"].min() >= 0
    assert len(daily) > 0
    assert len(monthly) > 0


def test_transform_weather(sample_weather_df):
    result = transform_weather(sample_weather_df)
    assert len(result) == 2
    assert result["temp_max"].iloc[0] == 20.0
