"""Generate reproducible EDA tables and an interactive HTML report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from .oulad_schema import NUMERIC_FEATURES


def run_eda(input_csv: Path, output_dir: Path) -> dict:
    frame = pd.read_csv(input_csv)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = (
        frame.isna().mean().mul(100).rename("missing_pct").sort_values(ascending=False).reset_index()
    )
    missing.columns = ["column", "missing_pct"]
    missing.to_csv(output_dir / "missingness.csv", index=False)

    numeric_summary = frame[NUMERIC_FEATURES].describe(
        percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
    ).T.reset_index().rename(columns={"index": "feature"})
    numeric_summary.to_csv(output_dir / "numeric_summary.csv", index=False)

    outcomes = (
        frame.groupby(["code_presentation", "code_module", "final_result"], observed=True)
        .size().rename("rows").reset_index()
    )
    outcomes.to_csv(output_dir / "outcomes_by_cohort.csv", index=False)

    adverse_by_module = (
        frame.groupby("code_module", observed=True)["adverse_outcome"]
        .agg(rows="size", adverse_rate="mean").reset_index()
    )
    adverse_by_module.to_csv(output_dir / "adverse_rate_by_module.csv", index=False)

    summary = {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "duplicate_student_module_presentation": int(
            frame.duplicated(["code_module", "code_presentation", "id_student"]).sum()
        ),
        "adverse_outcome_rows": int(frame["adverse_outcome"].sum()),
        "adverse_outcome_rate": float(frame["adverse_outcome"].mean()),
        "presentations": sorted(frame["code_presentation"].unique().tolist()),
        "modules": sorted(frame["code_module"].unique().tolist()),
    }
    (output_dir / "eda_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    outcome_counts = frame["final_result"].value_counts().rename_axis("outcome").reset_index(name="rows")
    fig1 = px.bar(outcome_counts, x="outcome", y="rows", color="outcome", title="Later final outcomes")
    fig2 = px.bar(
        adverse_by_module,
        x="code_module",
        y="adverse_rate",
        hover_data=["rows"],
        title="Observed adverse-outcome rate by module",
    )

    report = make_subplots(rows=2, cols=1, subplot_titles=("Later final outcomes", "Adverse-outcome rate by module"))
    for trace in fig1.data:
        report.add_trace(trace, row=1, col=1)
    report.add_trace(
        go.Bar(x=adverse_by_module["code_module"], y=adverse_by_module["adverse_rate"], name="Adverse rate"),
        row=2,
        col=1,
    )
    report.update_layout(height=850, title="OULAD Day-40 Exploratory Report", showlegend=False)
    report.update_yaxes(tickformat=".0%", row=2, col=1)
    report.write_html(output_dir / "eda_report.html", include_plotlyjs="cdn")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OULAD EDA artifacts")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/eda"))
    args = parser.parse_args()
    print(json.dumps(run_eda(args.input_csv, args.output_dir), indent=2))


if __name__ == "__main__":
    main()

