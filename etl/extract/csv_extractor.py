from pathlib import Path

import pandas as pd
from loguru import logger

from etl.config import get_settings

CSV_SOURCES = {
    "co_ppm_ohiggins_last_year.csv": {"pollutant": "CO", "unit": "ppm"},
    "mp10_ug-m3_ohiggins_last_year.csv": {"pollutant": "MP10", "unit": "ug/m3"},
    "mp25_ohiggins_ly.csv": {"pollutant": "MP25", "unit": "ug/m3"},
    "no2_ppb_ohiggins_ly.csv": {"pollutant": "NO2", "unit": "ppb"},
    "o3_ppb_ohiggins_ly.csv": {"pollutant": "O3", "unit": "ppb"},
}

COLUMN_MAP = {
    "FECHA (YYMMDD)": "fecha",
    "HORA (HHMM)": "hora",
    "Registros validados": "valor_validado",
    "Registros preliminares": "valor_preliminar",
    "Registros no validados": "valor_no_validado",
}


def _validate_csv_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"archivo csv no encontrado: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"archivo csv vacio o corrupto: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            header = f.readline()
        if "FECHA" not in header:
            raise ValueError(f"encabezado invalido en {path}")
    except UnicodeDecodeError as exc:
        raise ValueError(f"archivo csv corrupto (encoding): {path}") from exc


def extract_csv(path: Path, pollutant: str, unit: str) -> pd.DataFrame:
    _validate_csv_file(path)
    df = pd.read_csv(path, sep=";", decimal=",", encoding="utf-8")
    df.columns = [c.strip().rstrip(";") for c in df.columns]
    df = df.rename(columns=COLUMN_MAP)
    df["pollutant"] = pollutant
    df["unit"] = unit
    logger.info(f"extraidos {len(df)} registros de {path.name}")
    return df


def extract_all_csv(raw_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    settings = get_settings()
    source_dir = raw_dir or settings.raw_data_dir
    results: dict[str, pd.DataFrame] = {}
    for filename, meta in CSV_SOURCES.items():
        filepath = source_dir / filename
        if not filepath.exists():
            filepath = settings.raw_data_dir / filename
        results[meta["pollutant"]] = extract_csv(
            filepath, meta["pollutant"], meta["unit"]
        )
    return results
