"""Attach transparent, faculty-reviewed support suggestions to predictions."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .interventions import suggest_oulad_interventions


def add_support_suggestions(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    all_indicators = []
    all_suggestions = []
    for record in result.to_dict(orient="records"):
        recommendations = suggest_oulad_interventions(record)
        all_indicators.append(" | ".join(item["indicator"] for item in recommendations))
        all_suggestions.append(" | ".join(item["suggestion"] for item in recommendations))
    result["support_indicators"] = all_indicators
    result["faculty_review_options"] = all_suggestions
    result["review_status"] = "Not reviewed"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a faculty-review queue")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    frame = pd.read_csv(args.input_csv)
    output = add_support_suggestions(frame)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_csv, index=False)
    print(f"Wrote {len(output):,} review records")


if __name__ == "__main__":
    main()

