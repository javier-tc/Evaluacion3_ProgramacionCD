from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from etl.config import get_settings
from etl.extract.csv_extractor import extract_all_csv
from etl.extract.weather_extractor import extract_weather


def run_extraction() -> tuple[dict[str, pd.DataFrame], pd.DataFrame, Path]:
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = settings.raw_data_dir / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"iniciando extraccion - snapshot: {snapshot_dir}")
    pollution_dfs = extract_all_csv()
    for pollutant, df in pollution_dfs.items():
        df.to_csv(snapshot_dir / f"pollution_{pollutant}.csv", index=False)

    weather_df = extract_weather(save_path=snapshot_dir / "weather_api.json")
    weather_df.to_csv(snapshot_dir / "weather.csv", index=False)

    logger.info("extraccion completada")
    return pollution_dfs, weather_df, snapshot_dir
