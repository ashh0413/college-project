"""Train and evaluate calibrated OULAD early-warning models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .oulad_schema import (
    AUDIT_COLUMNS,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    assert_feature_contract,
)


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ], sparse_threshold=0)


def model_candidates(random_state: int):
    return {
        "dummy_prior": DummyClassifier(strategy="prior"),
        "logistic_regression": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=350,
            min_samples_leaf=4,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=250,
            learning_rate=0.07,
            max_leaf_nodes=20,
            min_samples_leaf=30,
            l2_regularization=1.0,
            class_weight="balanced",
            random_state=random_state,
        ),
    }


def capacity_threshold(probability: np.ndarray, target: np.ndarray, max_rate: float) -> dict:
    """Maximize recall while keeping the alert rate within a declared capacity."""
    best = None
    for threshold in np.unique(probability):
        selected = probability >= threshold
        rate = float(selected.mean())
        if rate == 0 or rate > max_rate + 1e-12:
            continue
        recall = recall_score(target, selected, zero_division=0)
        precision = precision_score(target, selected, zero_division=0)
        candidate = {
            "threshold": float(threshold),
            "selection_rate": rate,
            "recall": float(recall),
            "precision": float(precision),
        }
        if best is None or (candidate["recall"], candidate["precision"], -threshold) > (
            best["recall"], best["precision"], -best["threshold"]
        ):
            best = candidate
    if best is None:
        return {"threshold": 1.0, "selection_rate": 0.0, "recall": 0.0, "precision": 0.0}
    return best


def probability_metrics(target, probability) -> dict:
    return {
        "roc_auc": float(roc_auc_score(target, probability)),
        "average_precision": float(average_precision_score(target, probability)),
        "brier_score": float(brier_score_loss(target, probability)),
        "log_loss": float(log_loss(target, np.column_stack([1 - probability, probability]), labels=[0, 1])),
    }


def tier_probabilities(probability, low_threshold: float, high_threshold: float) -> np.ndarray:
    return np.where(
        probability >= high_threshold,
        "High",
        np.where(probability >= low_threshold, "Medium", "Low"),
    )


def tier_metrics(target: np.ndarray, tiers: np.ndarray) -> dict:
    high = tiers == "High"
    elevated = np.isin(tiers, ["Medium", "High"])
    return {
        "high_risk_recall": float(recall_score(target, high, zero_division=0)),
        "high_risk_precision": float(precision_score(target, high, zero_division=0)),
        "high_risk_f1": float(f1_score(target, high, zero_division=0)),
        "high_review_rate": float(high.mean()),
        "elevated_risk_recall": float(recall_score(target, elevated, zero_division=0)),
        "elevated_risk_precision": float(precision_score(target, elevated, zero_division=0)),
        "elevated_review_rate": float(elevated.mean()),
        "high_binary_confusion_matrix": confusion_matrix(target, high, labels=[0, 1]).tolist(),
    }


def fairness_audit(frame: pd.DataFrame, minimum_group_size: int) -> pd.DataFrame:
    records = []
    for attribute in ["gender", "age_band", "disability", "highest_education"]:
        for group, part in frame.groupby(attribute, dropna=False, observed=True):
            if len(part) < minimum_group_size:
                continue
            actual = part[TARGET_COLUMN].to_numpy()
            high = part["risk_tier"].eq("High").to_numpy()
            elevated = part["risk_tier"].isin(["Medium", "High"]).to_numpy()
            negatives = actual == 0
            false_positive_rate = float((high & negatives).sum() / negatives.sum()) if negatives.sum() else np.nan
            records.append({
                "attribute": attribute,
                "group": str(group),
                "rows": int(len(part)),
                "observed_adverse_rate": float(actual.mean()),
                "high_selection_rate": float(high.mean()),
                "high_recall": float(recall_score(actual, high, zero_division=0)),
                "high_precision": float(precision_score(actual, high, zero_division=0)),
                "high_false_positive_rate": false_positive_rate,
                "elevated_selection_rate": float(elevated.mean()),
                "elevated_recall": float(recall_score(actual, elevated, zero_division=0)),
            })
    return pd.DataFrame(records)


def fit_calibrated(pipeline, x_train, y_train, groups, is_dummy: bool):
    if is_dummy:
        return pipeline.fit(x_train, y_train)
    splits = list(GroupKFold(n_splits=2).split(x_train, y_train, groups=groups))
    calibrated = CalibratedClassifierCV(pipeline, method="sigmoid", cv=splits, n_jobs=-1)
    return calibrated.fit(x_train, y_train)


def run_training(input_csv: Path, config_path: Path, output_dir: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    frame = pd.read_csv(input_csv)
    assert_feature_contract(FEATURE_COLUMNS)

    train = frame[frame["code_presentation"].isin(config["train_presentations"])].copy()
    validation = frame[frame["code_presentation"].isin(config["validation_presentations"])].copy()
    test = frame[frame["code_presentation"].isin(config["test_presentations"])].copy()
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("One or more chronological data splits are empty")

    x_train, y_train = train[FEATURE_COLUMNS], train[TARGET_COLUMN].astype(int)
    x_validation, y_validation = validation[FEATURE_COLUMNS], validation[TARGET_COLUMN].astype(int)
    x_test, y_test = test[FEATURE_COLUMNS], test[TARGET_COLUMN].astype(int)

    fitted = {}
    comparison_records = []
    validation_details = {}
    for name, classifier in model_candidates(config["random_state"]).items():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("classifier", classifier)])
        estimator = fit_calibrated(
            pipeline,
            x_train,
            y_train,
            groups=train["code_presentation"],
            is_dummy=name == "dummy_prior",
        )
        fitted[name] = estimator
        probability = estimator.predict_proba(x_validation)[:, 1]
        high = capacity_threshold(probability, y_validation.to_numpy(), config["max_high_review_rate"])
        elevated = capacity_threshold(probability, y_validation.to_numpy(), config["max_elevated_review_rate"])
        metrics = probability_metrics(y_validation, probability)
        metrics.update({
            "high_risk_recall": high["recall"],
            "high_risk_precision": high["precision"],
            "high_review_rate": high["selection_rate"],
            "high_threshold": high["threshold"],
            "low_threshold": elevated["threshold"],
        })
        validation_details[name] = metrics
        comparison_records.append({"model": name, **metrics})

    eligible = [name for name in fitted if name != "dummy_prior"]
    selected_name = max(
        eligible,
        key=lambda name: (
            validation_details[name]["high_risk_recall"],
            validation_details[name]["average_precision"],
            -validation_details[name]["brier_score"],
        ),
    )
    selected = fitted[selected_name]
    high_threshold = validation_details[selected_name]["high_threshold"]
    low_threshold = validation_details[selected_name]["low_threshold"]

    test_probability = selected.predict_proba(x_test)[:, 1]
    test_tiers = tier_probabilities(test_probability, low_threshold, high_threshold)
    test_metrics = probability_metrics(y_test, test_probability)
    test_metrics.update(tier_metrics(y_test.to_numpy(), test_tiers))

    prediction_columns = [
        "code_module", "code_presentation", "id_student", "final_result", TARGET_COLUMN,
        *AUDIT_COLUMNS, *FEATURE_COLUMNS,
    ]
    prediction_columns = list(dict.fromkeys(prediction_columns))
    predictions = test[prediction_columns].copy()
    predictions["adverse_probability"] = test_probability
    predictions["risk_tier"] = test_tiers

    fairness = fairness_audit(predictions, config["minimum_fairness_group_size"])
    risk_summary = predictions.groupby("risk_tier", observed=True).agg(
        rows=("id_student", "size"),
        observed_adverse_rate=(TARGET_COLUMN, "mean"),
        mean_predicted_probability=("adverse_probability", "mean"),
    ).reindex(["Low", "Medium", "High"]).reset_index()

    fraction_positive, mean_predicted = calibration_curve(
        y_test, test_probability, n_bins=10, strategy="quantile"
    )
    calibration = pd.DataFrame({
        "mean_predicted_probability": mean_predicted,
        "observed_adverse_fraction": fraction_positive,
    })

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(comparison_records).to_csv(output_dir / "model_comparison.csv", index=False)
    predictions.to_csv(output_dir / "test_predictions.csv", index=False)
    fairness.to_csv(output_dir / "fairness_audit.csv", index=False)
    risk_summary.to_csv(output_dir / "risk_tier_summary.csv", index=False)
    calibration.to_csv(output_dir / "calibration_curve.csv", index=False)

    bundle = {
        "model": selected,
        "selected_model": selected_name,
        "feature_columns": FEATURE_COLUMNS,
        "low_threshold": low_threshold,
        "high_threshold": high_threshold,
        "cutoff_day": config["cutoff_day"],
        "classes": selected.classes_.tolist(),
        "warning": "Research prototype; faculty review is required before any support action.",
    }
    joblib.dump(bundle, output_dir / "model_bundle.joblib")
    x_train.sample(min(100, len(x_train)), random_state=config["random_state"]).to_csv(
        output_dir / "shap_background.csv", index=False
    )

    result = {
        "status": "research evaluation complete",
        "selected_model": selected_name,
        "selection_data": "validation presentations only",
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_rows": int(len(test)),
        "low_threshold": float(low_threshold),
        "high_threshold": float(high_threshold),
        "validation_metrics": validation_details,
        "test_metrics": test_metrics,
        "claim_boundary": "Historical public-data association; no causal or local deployment claim.",
    }
    (output_dir / "evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir / "feature_contract.json").write_text(json.dumps({
        "prediction_features": FEATURE_COLUMNS,
        "excluded_sensitive_audit_fields": AUDIT_COLUMNS,
        "target": TARGET_COLUMN,
    }, indent=2), encoding="utf-8")

    comparison = pd.DataFrame(comparison_records)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Validation comparison", "Test calibration"))
    fig.add_trace(go.Bar(
        x=comparison["model"], y=comparison["high_risk_recall"], name="High-tier recall"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=calibration["mean_predicted_probability"],
        y=calibration["observed_adverse_fraction"],
        mode="lines+markers",
        name="Selected model",
    ), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration"), row=1, col=2)
    fig.update_layout(height=500, title="Model Evaluation Report")
    fig.write_html(output_dir / "model_report.html", include_plotlyjs="cdn")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Train OULAD early-warning models")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/oulad_model.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/oulad"))
    args = parser.parse_args()
    print(json.dumps(run_training(args.input_csv, args.config, args.output_dir), indent=2))


if __name__ == "__main__":
    main()

