import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger
from pydantic import ValidationError

from etl.config import get_settings
from etl.validation.schemas import PollutionRecord, WeatherRecord

try:
    import great_expectations as gx
    GE_AVAILABLE = True
except ImportError:
    GE_AVAILABLE = False


def _validate_pydantic_pollution(df: pd.DataFrame) -> tuple[int, list[str]]:
    errors: list[str] = []
    valid_count = 0
    for i, row in df.iterrows():
        try:
            PollutionRecord(**row.to_dict())
            valid_count += 1
        except ValidationError as e:
            errors.append(f"fila {i}: {e}")
    return valid_count, errors


def _validate_pydantic_weather(df: pd.DataFrame) -> tuple[int, list[str]]:
    errors: list[str] = []
    valid_count = 0
    for i, row in df.iterrows():
        try:
            data = row.to_dict()
            if pd.isna(data.get("weather_code")):
                data["weather_code"] = None
            else:
                data["weather_code"] = int(data["weather_code"])
            WeatherRecord(**data)
            valid_count += 1
        except ValidationError as e:
            errors.append(f"fila {i}: {e}")
    return valid_count, errors


def _run_great_expectations(df: pd.DataFrame, suite_name: str) -> dict:
    if not GE_AVAILABLE or df.empty:
        return {"suite": suite_name, "success": True, "skipped": True}

    results = {"suite": suite_name, "success": True, "expectations": []}

    try:
        context = gx.get_context(mode="ephemeral")
        validator = context.sources.pandas_default.read_dataframe(df)

        if suite_name == "pollution" and "value" in df.columns:
            exp = validator.expect_column_values_to_not_be_null("value")
            results["expectations"].append({"name": "not_null_value", "success": exp.success})
            exp2 = validator.expect_column_values_to_be_between("value", min_value=0)
            results["expectations"].append({"name": "non_negative_value", "success": exp2.success})
        elif suite_name == "weather" and "date" in df.columns:
            exp = validator.expect_column_values_to_not_be_null("date")
            results["expectations"].append({"name": "not_null_date", "success": exp.success})

        results["success"] = all(e.get("success", True) for e in results["expectations"])
    except Exception as exc:
        results["success"] = False
        results["error"] = str(exc)

    return results


def validate_datasets(
    pollution_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    output_dir: Path | None = None,
) -> dict:
    settings = get_settings()
    report_dir = output_dir or (settings.processed_data_dir / "validation_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    poll_valid, poll_errors = _validate_pydantic_pollution(pollution_df)
    weather_valid, weather_errors = _validate_pydantic_weather(weather_df)

    dup_count = pollution_df.duplicated(subset=["measured_at", "pollutant"]).sum()

    ge_poll = _run_great_expectations(pollution_df, "pollution")
    ge_weather = _run_great_expectations(weather_df, "weather")

    report = {
        "timestamp": datetime.now().isoformat(),
        "pollution": {
            "total_records": len(pollution_df),
            "pydantic_valid": poll_valid,
            "pydantic_errors": poll_errors[:20],
            "duplicates": int(dup_count),
            "great_expectations": ge_poll,
        },
        "weather": {
            "total_records": len(weather_df),
            "pydantic_valid": weather_valid,
            "pydantic_errors": weather_errors[:20],
            "great_expectations": ge_weather,
        },
        "overall_success": (
            poll_valid == len(pollution_df)
            and weather_valid == len(weather_df)
            and dup_count == 0
            and ge_poll.get("success", True)
            and ge_weather.get("success", True)
        ),
    }

    report_path = report_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"reporte validacion guardado en {report_path}")
    if not report["overall_success"]:
        logger.warning("validacion con advertencias - revisar reporte")

    return report
