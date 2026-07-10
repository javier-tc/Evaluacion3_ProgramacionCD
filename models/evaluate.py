from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def regression_metrics(y_true, y_pred) -> dict:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else 0.0,
    }


def classification_metrics(y_true, y_pred) -> dict:
    labels = sorted(set(y_true) | set(y_pred))
    matrix = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "labels": labels,
        "confusion_matrix": matrix,
    }


def summarize_cv(scores: np.ndarray | list[float]) -> dict:
    if len(scores) == 0:
        return {"cv_mean": None, "cv_std": None}
    arr = np.asarray(scores, dtype=float)
    return {
        "cv_mean": float(arr.mean()),
        "cv_std": float(arr.std()),
    }

