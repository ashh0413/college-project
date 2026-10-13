# Student Success Analytics and Early Warning System

**Subtitle:** A Machine Learning-Based Decision Support System for Early Academic Intervention

This MSc project develops a human-reviewed early-warning prototype. It estimates whether a student may currently need a low, medium, or high level of academic support, explains the model output, and suggests faculty-approved interventions. It does not make academic or disciplinary decisions.

## Current scope

The first milestone contains:

- a project charter and research questions;
- a proposed data dictionary;
- an explicit, configurable target-label definition;
- data validation and leakage safeguards;
- a baseline model-comparison pipeline;
- transparent intervention rules; and
- tests for the initial risk-label logic.

The public-data plan uses OULAD as the primary research dataset and keeps the UCI higher-education dataset as an optional, separate benchmark. See `docs/dataset_selection.md`.

No performance claims are made until approved institutional data is available and evaluated.

The completed public-data prototype and measured results are documented in `docs/final_project_report.md`. Results apply only to the stated OULAD historical test cohort.

## Repository layout

```text
config/              Model and target configuration
data/raw/            Approved source data (not committed)
data/processed/      Prepared data (not committed)
docs/                Proposal, scope, and data documentation
src/student_success/ Python package
tests/               Automated checks
artifacts/           Generated metrics and trained models (not committed)
```

## Data contract

Each modelling row represents one student at one defined prediction point, such as week 6 of a semester. Features must contain only information available on or before that date. End-of-term outcome columns are used only to create the training label and must never be model inputs.

See `docs/data_dictionary.md` for the proposed fields. Adjust them with the institution before data collection.
An empty import header is available at `data/student_snapshots_template.csv`, and `docs/data_request_checklist.md` lists the questions to settle before requesting records.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Prepare labels

The initial label policy is a research starting point, not an institutional rule:

```powershell
python -m student_success.labels data/raw/student_snapshots.csv data/processed/labelled_snapshots.csv
```

Review label distributions and individual examples with academic stakeholders before modelling.

## Build the OULAD day-40 snapshot

After placing the official OULAD CSV files in `data/raw/oulad`:

```powershell
$env:PYTHONPATH = "src"
python -m student_success.oulad_features data/raw/oulad data/processed/oulad_day40.csv --cutoff-day 40
```

The builder excludes withdrawals already recorded by the cutoff and aggregates only due assessments, observed submissions, and VLE activity available by that date.

## Train baseline models

```powershell
python -m student_success.train data/processed/labelled_snapshots.csv --output-dir artifacts
```

The pipeline uses a chronological holdout when `snapshot_date` is available, compares interpretable and tree-based baselines, and selects by **High-risk recall** with macro F1 as a tie-breaker. This is an initial technical benchmark; deployment requires calibration, subgroup fairness checks, drift monitoring, and faculty validation.

## Run the complete OULAD experiment

```powershell
$env:PYTHONPATH = "src"
python -m student_success.eda_oulad data/processed/oulad_day40.csv --output-dir artifacts/eda
python -m student_success.train_oulad data/processed/oulad_day40.csv --config config/oulad_model.json --output-dir artifacts/oulad
python -m student_success.support_outputs artifacts/oulad/test_predictions.csv artifacts/oulad/faculty_review_queue.csv
python -m student_success.explain_oulad --output-dir artifacts/oulad/explanations --rows-per-tier 25
```

## Launch the dashboard

```powershell
$env:PYTHONPATH = "src"
streamlit run dashboard/app.py
```

The dashboard contains separate Faculty, Student, and Evaluation views. The Student view intentionally omits the model risk tier and focuses on learning records and support resources.

Alternatively, run `run_dashboard.ps1`. To reproduce the modelling and reporting pipeline after setup, run `run_all.ps1`. It reuses the existing 27,042-row day-40 dataset by default, avoiding another read of the 453 MB VLE file.

Use `run_all.ps1 -RebuildData` only after changing the raw OULAD files or feature-engineering code. That option rereads the large VLE file and prints chunk progress. Use `run_all.ps1 -SkipShap` for a quicker model/test run when the existing SHAP artifacts do not need to be regenerated.

## Final documentation

- `docs/final_project_report.md` — dissertation-ready project report
- `docs/model_card.md` — intended use, measured performance, and risks
- `docs/privacy_ethics_protocol.md` — governance and human-review requirements
- `docs/dataset_selection.md` — dataset choice and claim boundaries

## Responsible-use boundary

- Predictions are indicators, not facts or diagnoses.
- Faculty must verify the data and context before acting.
- Recommended actions must be supportive and proportionate.
- Sensitive attributes are excluded from prediction by default and may be used separately for authorized fairness audits.
- The system must not automatically alter grades, attendance, enrolment, discipline, scholarships, or access to services.
