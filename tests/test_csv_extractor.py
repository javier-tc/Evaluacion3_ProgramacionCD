from pathlib import Path

import pandas as pd
import pytest

from etl.extract.csv_extractor import CSV_SOURCES, extract_all_csv, extract_csv


def test_extract_csv_valid(raw_csv_dir):
    filename = "mp25_ohiggins_ly.csv"
    meta = CSV_SOURCES[filename]
    df = extract_csv(raw_csv_dir / filename, meta["pollutant"], meta["unit"])
    assert len(df) > 0
    assert "pollutant" in df.columns
    assert df["pollutant"].iloc[0] == "MP25"


def test_extract_all_csv(raw_csv_dir):
    results = extract_all_csv(raw_csv_dir)
    assert len(results) == 5
    assert "CO" in results
    assert "O3" in results


def test_extract_csv_not_found():
    with pytest.raises(FileNotFoundError):
        extract_csv(Path("/no/existe.csv"), "CO", "ppm")


def test_extract_csv_corrupt(tmp_path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text("")
    with pytest.raises(ValueError):
        extract_csv(bad_file, "CO", "ppm")
