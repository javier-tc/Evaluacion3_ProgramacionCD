#!/usr/bin/env python3
"""orquestador principal del pipeline etl."""

import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from etl.config import get_settings
from etl.extract.orchestrator import run_extraction
from etl.load.db_loader import load_all_data
from etl.models import EtlExecutionLog, get_session_factory
from etl.transform.pollution_transformer import compute_correlations, transform_pollution
from etl.transform.weather_transformer import transform_weather
from etl.validation.validator import validate_datasets
from scripts.migrate import migrate


def _log_etl_stage(run_id: str, stage: str, status: str, records: int = 0,
                   error: str | None = None, duration: float | None = None):
    Session = get_session_factory()
    with Session() as session:
        session.add(EtlExecutionLog(
            run_id=run_id,
            stage=stage,
            status=status,
            records_count=records,
            error_message=error,
            duration_seconds=duration,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        ))
        session.commit()


def run_pipeline() -> None:
    run_id = str(uuid.uuid4())[:8]
    settings = get_settings()
    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"=== inicio pipeline etl (run_id={run_id}) ===")
    t0 = time.time()

    try:
        migrate()

        t_extract = time.time()
        pollution_dfs, weather_raw, _ = run_extraction()
        _log_etl_stage(run_id, "extract", "success",
                       sum(len(d) for d in pollution_dfs.values()) + len(weather_raw),
                       duration=time.time() - t_extract)

        t_transform = time.time()
        pollution_df, daily_df, monthly_df = transform_pollution(pollution_dfs)
        weather_df = transform_weather(weather_raw)
        correlation_df = compute_correlations(pollution_df, weather_df)

        pollution_df.to_parquet(settings.processed_data_dir / "pollution.parquet", index=False)
        weather_df.to_parquet(settings.processed_data_dir / "weather.parquet", index=False)
        daily_df.to_parquet(settings.processed_data_dir / "daily_metrics.parquet", index=False)
        monthly_df.to_parquet(settings.processed_data_dir / "monthly_metrics.parquet", index=False)
        correlation_df.to_parquet(settings.processed_data_dir / "correlations.parquet", index=False)
        _log_etl_stage(run_id, "transform", "success", len(pollution_df),
                       duration=time.time() - t_transform)

        t_validate = time.time()
        report = validate_datasets(pollution_df, weather_df)
        _log_etl_stage(run_id, "validate", "success" if report["overall_success"] else "warning",
                       len(pollution_df), duration=time.time() - t_validate)

        t_load = time.time()
        total = load_all_data(
            pollution_df, weather_df, daily_df, monthly_df, correlation_df, run_id
        )
        _log_etl_stage(run_id, "pipeline", "success", total, duration=time.time() - t0)

        logger.info(f"=== pipeline etl completado en {time.time() - t0:.2f}s ===")

    except Exception as exc:
        _log_etl_stage(run_id, "pipeline", "failed", error=str(exc),
                       duration=time.time() - t0)
        logger.exception(f"pipeline etl fallido: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
