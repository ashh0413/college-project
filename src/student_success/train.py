"""Baseline model comparison with High-risk recall as the primary criterion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .schema import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, TARGET_COLUMN, assert_no_leakage
from .validation import validate_snapshot_data


def chronological_split(frame: pd.DataFrame, test_fraction: float):
    ordered = frame.assign(_date=pd.to_datetime(frame["snapshot_date"])).sort_values("_date")
    cut = max(1, int(len(ordered) * (1 - test_fraction)))
    return ordered.iloc[:cut].drop(columns="_date"), ordered.iloc[cut:].drop(columns="_date")


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])


def evaluate(model, x_test, y_test) -> dict:
    predictions = model.predict(x_test)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return {
        "high_risk_recall": recall_score(y_test, predictions, labels=["High"], average="macro", zero_division=0),
        "macro_f1": report["macro avg"]["f1-score"],
        "classification_report": report,
        "confusion_matrix_labels": ["Low", "Medium", "High"],
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=["Low", "Medium", "High"]).tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline student-support risk models")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/project_config.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    frame = pd.read_csv(args.input_csv).dropna(subset=[TARGET_COLUMN])
    issues = validate_snapshot_data(frame)
    if issues:
        raise ValueError("Dataset validation failed:\n- " + "\n- ".join(issues))

    assert_no_leakage(FEATURE_COLUMNS)
    train, test = chronological_split(frame, config["model_selection"]["test_fraction"])
    x_train, y_train = train[FEATURE_COLUMNS], train[TARGET_COLUMN]
    x_test, y_test = test[FEATURE_COLUMNS], test[TARGET_COLUMN]

    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=config["model_selection"]["random_state"],
        ),
    }

    results = {}
    fitted = {}
    for name, classifier in models.items():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("model", classifier)])
        pipeline.fit(x_train, y_train)
        fitted[name] = pipeline
        results[name] = evaluate(pipeline, x_test, y_test)

    ranked = sorted(results, key=lambda name: (
        results[name]["high_risk_recall"], results[name]["macro_f1"]
    ), reverse=True)
    best_name = ranked[0]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted[best_name], args.output_dir / "baseline_model.joblib")
    payload = {
        "warning": "Research benchmark only; predictions require faculty review.",
        "train_rows": len(train),
        "test_rows": len(test),
        "selected_model": best_name,
        "selection_rule": "High-risk recall, then macro F1",
        "models": results,
    }
    (args.output_dir / "baseline_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

