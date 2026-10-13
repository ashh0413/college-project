"""Create research labels from post-snapshot academic outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REQUIRED_OUTCOMES = {
    "previous_gpa",
    "end_term_failed_subjects",
    "end_term_gpa",
    "withdrew",
}


def assign_risk_labels(frame: pd.DataFrame, policy: dict) -> pd.Series:
    """Return Low/Medium/High support-risk proxies using an explicit policy."""
    missing = sorted(REQUIRED_OUTCOMES.difference(frame.columns))
    if missing:
        raise ValueError(f"Cannot create labels; missing columns: {missing}")

    failed = pd.to_numeric(frame["end_term_failed_subjects"], errors="coerce")
    end_gpa = pd.to_numeric(frame["end_term_gpa"], errors="coerce")
    previous_gpa = pd.to_numeric(frame["previous_gpa"], errors="coerce")
    withdrew = frame["withdrew"].astype("string").str.lower().isin({"true", "1", "yes"})
    decline = previous_gpa - end_gpa

    unknown = failed.isna() | end_gpa.isna() | previous_gpa.isna()
    high = (
        withdrew
        | (failed >= policy["high_failed_subjects_min"])
        | (end_gpa < policy["high_end_term_gpa_below"])
    )
    medium = (
        (failed >= policy["medium_failed_subjects_min"])
        | (decline >= policy["medium_gpa_decline_at_least"])
    ) & ~high

    labels = pd.Series("Low", index=frame.index, dtype="string")
    labels.loc[medium] = "Medium"
    labels.loc[high] = "High"
    labels.loc[unknown & ~withdrew] = pd.NA
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Create risk labels from end-term outcomes")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/project_config.json"))
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    frame = pd.read_csv(args.input_csv)
    frame["risk_label"] = assign_risk_labels(frame, config["label_policy"])
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_csv, index=False)
    print(frame["risk_label"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()

