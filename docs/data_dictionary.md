# Proposed Data Dictionary

This is a starting schema for institutional review. Fields should be removed unless they are necessary, lawful, consistently recorded, and available at prediction time.

## Identifiers and timing

| Field | Type | Purpose | Model input? |
|---|---|---|---|
| `student_id` | string | De-identified stable identifier | No |
| `snapshot_date` | date | Date on which features were available | No |
| `academic_year` | string | Enables chronological evaluation | No |
| `programme` | category | Academic context | Yes, subject to review |
| `semester` | integer | Current semester | Yes |

## Prediction-time academic features

| Field | Type | Expected range/meaning |
|---|---|---|
| `attendance_pct` | float | 0–100 attendance available by snapshot |
| `attendance_change_4w` | float | Percentage-point change over four weeks |
| `consecutive_absences` | integer | Current consecutive absence count |
| `assessment_avg` | float | 0–100 average of completed assessments |
| `assessment_change` | float | Change from the previous comparable period |
| `assignment_completion_pct` | float | 0–100 completed assignment percentage |
| `late_submissions` | integer | Count available by snapshot |
| `previous_gpa` | float | Previous-semester GPA |
| `cumulative_gpa` | float | GPA known at the snapshot date |
| `gpa_change` | float | Change from prior semester |
| `backlog_count` | integer | Backlogs known at the snapshot date |
| `failed_subjects_previous` | integer | Prior failed-subject count |
| `credits_registered` | float | Current academic workload |

## End-of-term outcomes used only for training labels

| Field | Type | Meaning | Model input? |
|---|---|---|---|
| `end_term_failed_subjects` | integer | Failed subjects after the prediction point | Never |
| `end_term_gpa` | float | GPA measured at the end of the term | Never |
| `withdrew` | boolean | Whether the student withdrew after the snapshot | Never |

## Derived target

| Field | Type | Values |
|---|---|---|
| `risk_label` | category | `Low`, `Medium`, `High` |

## Sensitive attributes

Sensitive attributes must not be included automatically. If institutional approval permits fairness evaluation, they should be kept in a separately controlled audit dataset and not supplied to the prediction pipeline by default.

## Data-quality checks

- One row per student per approved snapshot point
- No duplicate `student_id` and `snapshot_date` pairs
- Percentages within 0–100
- Counts non-negative
- Snapshot dates earlier than measured outcomes
- Missingness documented by field and group
- Consistent GPA scale across records
- No names, phone numbers, email addresses, addresses, or free-text faculty notes in model data

