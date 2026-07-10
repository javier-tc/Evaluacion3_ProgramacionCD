#!/usr/bin/env python3
"""entrena modelos predictivos desde la base de datos."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from etl.models import get_session_factory
from models.features import fetch_training_frame_from_db
from models.registry import persist_model_metrics, save_training_results
from models.train_classification import train_classification_models
from models.train_regression import train_regression_models
from scripts.migrate import migrate


def run_training() -> list[dict]:
    started = time.time()
    migrate()
    Session = get_session_factory()

    with Session() as session:
        frame = fetch_training_frame_from_db(session)
        if frame.empty:
            raise ValueError("no hay datos suficientes para entrenar modelos")

        results = []
        results.extend(train_regression_models(frame))
        results.extend(train_classification_models(frame))

        metadata = save_training_results(results)
        persist_model_metrics(session, metadata)

    logger.info(f"entrenamiento completado en {time.time() - started:.2f}s")
    return metadata


if __name__ == "__main__":
    try:
        run_training()
    except Exception as exc:
        logger.exception(f"entrenamiento fallido: {exc}")
        sys.exit(1)

