"""Build leakage-aware early-warning snapshots from the OULAD CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


KEYS = ["code_module", "code_presentation", "id_student"]
SUCCESS_RESULTS = {"Pass", "Distinction"}
ADVERSE_RESULTS = {"Fail", "Withdrawn"}


def build_base_cohort(raw_dir: Path, cutoff_day: int) -> pd.DataFrame:
    """Return students registered and still active at the prediction cutoff."""
    info = pd.read_csv(raw_dir / "studentInfo.csv")
    registration = pd.read_csv(raw_dir / "studentRegistration.csv")
    cohort = info.merge(registration, on=KEYS, how="inner", validate="one_to_one")

    known_results = SUCCESS_RESULTS | ADVERSE_RESULTS
    cohort = cohort[cohort["final_result"].isin(known_results)].copy()
    cohort = cohort[
        cohort["date_registration"].le(cutoff_day)
        & (cohort["date_unregistration"].isna() | cohort["date_unregistration"].gt(cutoff_day))
    ].copy()

    cohort["adverse_outcome"] = cohort["final_result"].isin(ADVERSE_RESULTS).astype("int8")
    return cohort


def build_assessment_features(raw_dir: Path, cutoff_day: int) -> pd.DataFrame:
    """Aggregate assessments due and submitted by the prediction cutoff."""
    assessments = pd.read_csv(raw_dir / "assessments.csv")
    submissions = pd.read_csv(raw_dir / "studentAssessment.csv")

    due = assessments[
        assessments["date"].notna() & assessments["date"].le(cutoff_day)
    ].copy()
    observed = submissions.merge(
        due,
        on="id_assessment",
        how="inner",
        validate="many_to_one",
    )
    observed = observed[observed["date_submitted"].le(cutoff_day)].copy()
    observed["late_submission"] = observed["date_submitted"].gt(observed["date"])
    observed["weighted_score_component"] = observed["score"] * observed["weight"]

    submitted = observed.groupby(KEYS, as_index=False).agg(
        assessments_submitted=("id_assessment", "nunique"),
        assessment_score_mean=("score", "mean"),
        assessment_score_min=("score", "min"),
        late_assessments=("late_submission", "sum"),
        assessment_weight_submitted=("weight", "sum"),
        weighted_score_sum=("weighted_score_component", "sum"),
    )
    submitted["weighted_assessment_score"] = np.where(
        submitted["assessment_weight_submitted"].gt(0),
        submitted["weighted_score_sum"] / submitted["assessment_weight_submitted"],
        np.nan,
    )
    submitted = submitted.drop(columns="weighted_score_sum")

    due_counts = due.groupby(
        ["code_module", "code_presentation"], as_index=False
    ).agg(
        assessments_due=("id_assessment", "nunique"),
        assessment_weight_due=("weight", "sum"),
    )
    return submitted.merge(
        due_counts,
        on=["code_module", "code_presentation"],
        how="left",
        validate="many_to_one",
    )


def build_vle_features(
    raw_dir: Path,
    cutoff_day: int,
    chunksize: int = 1_000_000,
    show_progress: bool = False,
) -> pd.DataFrame:
    """Aggregate dated VLE activity without loading the full event table at once."""
    daily_partials: list[pd.DataFrame] = []
    usecols = KEYS + ["date", "sum_click"]

    processed_rows = 0
    for chunk_number, chunk in enumerate(
        pd.read_csv(raw_dir / "studentVle.csv", usecols=usecols, chunksize=chunksize),
        start=1,
    ):
        processed_rows += len(chunk)
        if show_progress:
            print(
                f"VLE chunk {chunk_number}: {processed_rows:,} source rows processed",
                flush=True,
            )
        chunk = chunk[chunk["date"].le(cutoff_day)].copy()
        if chunk.empty:
            continue

        daily_partials.append(
            chunk.groupby(KEYS + ["date"], as_index=False)["sum_click"].sum()
        )

    if not daily_partials:
        return pd.DataFrame(columns=KEYS)

    daily = pd.concat(daily_partials, ignore_index=True)
    daily = daily.groupby(KEYS + ["date"], as_index=False)["sum_click"].sum()
    daily["clicks_last_7d"] = daily["sum_click"].where(
        daily["date"].between(cutoff_day - 6, cutoff_day), 0
    )
    daily["clicks_previous_7d"] = daily["sum_click"].where(
        daily["date"].between(cutoff_day - 13, cutoff_day - 7), 0
    )
    daily["clicks_last_14d"] = daily["sum_click"].where(
        daily["date"].between(cutoff_day - 13, cutoff_day), 0
    )
    daily["active_last_14d"] = daily["date"].where(
        daily["date"].between(cutoff_day - 13, cutoff_day)
    )
    result = daily.groupby(KEYS, as_index=False).agg(
        total_clicks=("sum_click", "sum"),
        active_days=("date", "nunique"),
        last_activity_day=("date", "max"),
        clicks_last_7d=("clicks_last_7d", "sum"),
        clicks_previous_7d=("clicks_previous_7d", "sum"),
        clicks_last_14d=("clicks_last_14d", "sum"),
        active_days_last_14d=("active_last_14d", "nunique"),
    )
    result["days_since_last_activity"] = cutoff_day - result["last_activity_day"]
    result["click_trend_7d"] = result["clicks_last_7d"] - result["clicks_previous_7d"]
    return result


def build_snapshot(
    raw_dir: Path,
    cutoff_day: int = 40,
    show_progress: bool = False,
) -> pd.DataFrame:
    """Create one model-ready row per active student/module/presentation."""
    cohort = build_base_cohort(raw_dir, cutoff_day)
    assessment = build_assessment_features(raw_dir, cutoff_day)
    vle = build_vle_features(raw_dir, cutoff_day, show_progress=show_progress)

    snapshot = cohort.merge(assessment, on=KEYS, how="left")
    snapshot = snapshot.merge(vle, on=KEYS, how="left")

    zero_fill = [
        "assessments_submitted",
        "late_assessments",
        "assessment_weight_submitted",
        "total_clicks",
        "active_days",
        "clicks_last_7d",
        "clicks_previous_7d",
        "clicks_last_14d",
        "active_days_last_14d",
    ]
    for column in zero_fill:
        snapshot[column] = snapshot[column].fillna(0)

    snapshot["assessments_due"] = snapshot["assessments_due"].fillna(0)
    snapshot["assessment_weight_due"] = snapshot["assessment_weight_due"].fillna(0)
    snapshot["assessment_completion_rate"] = np.where(
        snapshot["assessments_due"].gt(0),
        snapshot["assessments_submitted"] / snapshot["assessments_due"],
        np.nan,
    )
    snapshot["assessment_weight_completion_rate"] = np.where(
        snapshot["assessment_weight_due"].gt(0),
        snapshot["assessment_weight_submitted"] / snapshot["assessment_weight_due"],
        np.nan,
    )
    snapshot["has_no_vle_activity"] = snapshot["last_activity_day"].isna().astype("int8")
    snapshot["days_since_last_activity"] = snapshot["days_since_last_activity"].fillna(cutoff_day + 1)
    snapshot["presentation_season"] = snapshot["code_presentation"].astype("string").str[-1]
    snapshot["cutoff_day"] = cutoff_day
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an OULAD early-warning snapshot")
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--cutoff-day", type=int, default=40)
    args = parser.parse_args()

    print(f"Building leakage-aware day-{args.cutoff_day} snapshot...", flush=True)
    snapshot = build_snapshot(args.raw_dir, args.cutoff_day, show_progress=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(args.output_csv, index=False)

    print(f"Rows: {len(snapshot):,}")
    print(f"Columns: {len(snapshot.columns)}")
    print("Outcome distribution:")
    print(snapshot["final_result"].value_counts().to_string())
    print("Adverse outcome distribution:")
    print(snapshot["adverse_outcome"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
