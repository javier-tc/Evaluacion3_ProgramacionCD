from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from models.config import MODEL_RANDOM_STATE, TARGET_COLUMN, WEATHER_FEATURES
from models.evaluate import regression_metrics, summarize_cv
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


def train_regression_models(frame) -> list[dict]:
    X, y = split_features_target(frame, TARGET_COLUMN)
    if len(X) < 8:
        raise ValueError("se requieren al menos 8 registros para entrenar regresion")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=MODEL_RANDOM_STATE,
    )

    candidates = {
        "linear_regression": LinearRegression(),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=120,
            max_depth=8,
            random_state=MODEL_RANDOM_STATE,
        ),
        "gradient_boosting_regressor": GradientBoostingRegressor(
            random_state=MODEL_RANDOM_STATE,
        ),
    }

    results = []
    cv_splits = min(5, len(X_train))
    for name, estimator in candidates.items():
        model = _pipeline(estimator)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        metrics = regression_metrics(y_test, predictions)

        cv_summary = {"cv_mean": None, "cv_std": None}
        if cv_splits >= 2:
            cv = KFold(n_splits=cv_splits, shuffle=True, random_state=MODEL_RANDOM_STATE)
            scores = cross_val_score(
                model,
                X,
                y,
                cv=cv,
                scoring="neg_mean_absolute_error",
            )
            cv_summary = summarize_cv(-scores)

        model.fit(X, y)
        results.append({
            "task_type": "regression",
            "model_name": name,
            "model": model,
            "metrics": metrics | cv_summary,
            "target": TARGET_COLUMN,
            "features": WEATHER_FEATURES,
        })

    return sorted(results, key=lambda item: item["metrics"]["mae"])

