from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
from sqlalchemy import delete
from sqlalchemy.orm import Session

from etl.models import ModelMetric
from models.config import ARTIFACT_DIR, ensure_artifact_dir


def save_model_result(result: dict, artifact_dir: Path = ARTIFACT_DIR) -> dict:
    artifact_dir = ensure_artifact_dir(artifact_dir)
    trained_at = datetime.now()
    stamp = trained_at.strftime("%Y%m%d_%H%M%S")
    task_type = result["task_type"]
    model_name = result["model_name"]
    path = artifact_dir / f"{stamp}_{task_type}_{model_name}.joblib"
    meta_path = path.with_suffix(".json")

    joblib.dump(result["model"], path)
    metadata = {
        "task_type": task_type,
        "model_name": model_name,
        "target": result["target"],
        "features": result["features"],
        "metrics": result["metrics"],
        "artifact_path": str(path),
        "trained_at": trained_at.isoformat(),
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def save_training_results(results: list[dict], artifact_dir: Path = ARTIFACT_DIR) -> list[dict]:
    return [save_model_result(result, artifact_dir) for result in results]


def persist_model_metrics(session: Session, metadata: list[dict]) -> None:
    session.execute(delete(ModelMetric))
    for item in metadata:
        metrics = item["metrics"]
        details = json.dumps(item, ensure_ascii=False)
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)) and metric_value is not None:
                session.add(ModelMetric(
                    task_type=item["task_type"],
                    model_name=item["model_name"],
                    metric_name=metric_name,
                    metric_value=float(metric_value),
                    artifact_path=item["artifact_path"],
                    details=details,
                    trained_at=datetime.fromisoformat(item["trained_at"]),
                ))
    session.commit()


def load_latest_metadata(task_type: str | None = None, artifact_dir: Path = ARTIFACT_DIR) -> dict[str, Any] | None:
    artifact_dir = ensure_artifact_dir(artifact_dir)
    files = sorted(artifact_dir.glob("*.json"), reverse=True)
    for path in files:
        metadata = json.loads(path.read_text(encoding="utf-8"))
        if task_type is None or metadata.get("task_type") == task_type:
            return metadata
    return None


def load_latest_model(task_type: str, artifact_dir: Path = ARTIFACT_DIR):
    metadata = load_latest_metadata(task_type, artifact_dir)
    if not metadata:
        return None, None
    return joblib.load(metadata["artifact_path"]), metadata

