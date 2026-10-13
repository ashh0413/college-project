"""Generate model-agnostic SHAP explanations for the selected OULAD model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import shap


def stratified_sample(frame: pd.DataFrame, rows_per_tier: int, random_state: int) -> pd.DataFrame:
    parts = []
    for _, part in frame.groupby("risk_tier", observed=True):
        parts.append(part.sample(min(rows_per_tier, len(part)), random_state=random_state))
    return pd.concat(parts).sort_index()


def run_explanations(
    bundle_path: Path,
    predictions_path: Path,
    background_path: Path,
    output_dir: Path,
    rows_per_tier: int = 30,
) -> dict:
    bundle = joblib.load(bundle_path)
    predictions = pd.read_csv(predictions_path)
    background = pd.read_csv(background_path)
    features = bundle["feature_columns"]
    model = bundle["model"]

    background = background[features].sample(min(25, len(background)), random_state=42)
    sample = stratified_sample(predictions, rows_per_tier, random_state=42)

    encoded_background = background.copy()
    encoded_sample = sample[features].copy()
    category_levels = {}
    for feature in features:
        if not (
            pd.api.types.is_object_dtype(encoded_background[feature])
            or pd.api.types.is_string_dtype(encoded_background[feature])
        ):
            continue
        levels = sorted(
            pd.concat([encoded_background[feature], encoded_sample[feature]])
            .fillna("__MISSING__").astype(str).unique().tolist()
        )
        category_levels[feature] = levels
        mapping = {value: index for index, value in enumerate(levels)}
        encoded_background[feature] = (
            encoded_background[feature].fillna("__MISSING__").astype(str).map(mapping).astype(float)
        )
        encoded_sample[feature] = (
            encoded_sample[feature].fillna("__MISSING__").astype(str).map(mapping).astype(float)
        )

    def predict_probability(values):
        data = pd.DataFrame(values, columns=features)
        for feature, levels in category_levels.items():
            codes = data[feature].round().clip(0, len(levels) - 1).astype(int)
            data[feature] = codes.map(dict(enumerate(levels))).replace("__MISSING__", pd.NA)
        return model.predict_proba(data)

    explainer = shap.Explainer(
        predict_probability,
        encoded_background.to_numpy(dtype=float),
        feature_names=features,
        algorithm="permutation",
        seed=42,
    )
    explanation = explainer(
        encoded_sample.to_numpy(dtype=float),
        max_evals=2 * len(features) + 1,
        batch_size=20,
    )

    class_index = bundle["classes"].index(1)
    values = explanation.values[:, :, class_index]
    global_table = pd.DataFrame({
        "feature": features,
        "mean_abs_shap": np.abs(values).mean(axis=0),
        "mean_shap": values.mean(axis=0),
    }).sort_values("mean_abs_shap", ascending=False)

    local_records = []
    for row_position, (_, row) in enumerate(sample.iterrows()):
        order = np.argsort(np.abs(values[row_position]))[::-1][:5]
        for rank, feature_index in enumerate(order, start=1):
            feature = features[feature_index]
            local_records.append({
                "code_module": row["code_module"],
                "code_presentation": row["code_presentation"],
                "id_student": row["id_student"],
                "risk_tier": row["risk_tier"],
                "rank": rank,
                "feature": feature,
                "feature_value": row[feature],
                "shap_value_for_adverse_outcome": values[row_position, feature_index],
                "direction": "increases estimated risk" if values[row_position, feature_index] > 0 else "decreases estimated risk",
            })

    output_dir.mkdir(parents=True, exist_ok=True)
    global_table.to_csv(output_dir / "shap_global.csv", index=False)
    pd.DataFrame(local_records).to_csv(output_dir / "shap_local_sample.csv", index=False)
    sample[["code_module", "code_presentation", "id_student", "risk_tier"]].to_csv(
        output_dir / "shap_explained_students.csv", index=False
    )

    chart = px.bar(
        global_table.head(15).sort_values("mean_abs_shap"),
        x="mean_abs_shap",
        y="feature",
        orientation="h",
        title="Global SHAP importance for adverse-outcome probability",
    )
    chart.write_html(output_dir / "shap_global.html", include_plotlyjs="cdn")

    metadata = {
        "method": "model-agnostic permutation SHAP",
        "explained_rows": int(len(sample)),
        "background_rows": int(len(background)),
        "output_explained": "calibrated probability of later Fail or Withdrawn",
        "causal_warning": "SHAP explains model behaviour and does not establish causes.",
    }
    (output_dir / "shap_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OULAD SHAP artifacts")
    parser.add_argument("--bundle", type=Path, default=Path("artifacts/oulad/model_bundle.joblib"))
    parser.add_argument("--predictions", type=Path, default=Path("artifacts/oulad/test_predictions.csv"))
    parser.add_argument("--background", type=Path, default=Path("artifacts/oulad/shap_background.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/oulad/explanations"))
    parser.add_argument("--rows-per-tier", type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(run_explanations(
        args.bundle, args.predictions, args.background, args.output_dir, args.rows_per_tier
    ), indent=2))


if __name__ == "__main__":
    main()
