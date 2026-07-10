from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from models.config import ALERT_TARGET_COLUMN, MODEL_RANDOM_STATE, WEATHER_FEATURES
from models.evaluate import classification_metrics, summarize_cv
from models.features import split_features_target


def _pipeline(estimator) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("numeric", StandardScaler(), WEATHER_FEATURES)],
        remainder="drop",
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", estimator),
    ])


def _can_stratify(y) -> bool:
    counts = y.value_counts()
    return len(counts) > 1 and counts.min() >= 2


def train_classification_models(frame) -> list[dict]:
    X, y = split_features_target(frame, ALERT_TARGET_COLUMN)
    if len(X) < 8 or y.nunique() < 2:
        raise ValueError("se requieren al menos 8 registros y 2 clases para clasificacion")

    stratify = y if _can_stratify(y) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=MODEL_RANDOM_STATE,
        stratify=stratify,
    )

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest_classifier": RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            random_state=MODEL_RANDOM_STATE,
        ),
        "svc_classifier": SVC(kernel="rbf", C=1.0, gamma="scale"),
    }

    results = []
    class_counts = y.value_counts()
    cv_splits = min(5, int(class_counts.min())) if len(class_counts) > 1 else 0
    for name, estimator in candidates.items():
        model = _pipeline(estimator)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        metrics = classification_metrics(y_test, predictions)

        cv_summary = {"cv_mean": None, "cv_std": None}
        if cv_splits >= 2:
            cv = StratifiedKFold(
                n_splits=cv_splits,
                shuffle=True,
                random_state=MODEL_RANDOM_STATE,
            )
            scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro")
            cv_summary = summarize_cv(scores)

        model.fit(X, y)
        results.append({
            "task_type": "classification",
            "model_name": name,
            "model": model,
            "metrics": metrics | cv_summary,
            "target": ALERT_TARGET_COLUMN,
            "features": WEATHER_FEATURES,
        })

    return sorted(results, key=lambda item: item["metrics"]["f1_macro"], reverse=True)

