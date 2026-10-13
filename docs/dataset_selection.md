# Public Dataset Selection

## Decision

Use the **Open University Learning Analytics Dataset (OULAD)** as the primary dataset. Use **UCI Predict Students' Dropout and Academic Success** only as a separate benchmark if time permits. Do not combine rows from the two datasets because they describe different institutions, students, collection processes, and outcomes.

## Why OULAD is the primary choice

OULAD contains anonymized higher-education records linking students, module presentations, assessments, assessment submissions, registration outcomes, and dated Virtual Learning Environment interactions. Its dated events allow us to construct an authentic early-warning snapshot, such as information available by day 40 after a module begins.

This supports the core MSc work:

- relational data integration;
- time-aware feature engineering;
- assessment and assignment-completion indicators;
- engagement trends from dated VLE activity;
- leakage-safe early prediction;
- Pass/Distinction versus Fail/Withdrawn outcomes;
- model comparison, SHAP, dashboards, and responsible-use analysis.

OULAD does not contain conventional classroom attendance, GPA, or backlog fields. The proposal must therefore describe VLE engagement, assessment submission, and previous-attempt information using the dataset's actual variables. It must not rename VLE clicks as attendance or invent GPA/backlogs.

## Proposed OULAD modelling design

### Unit of analysis

One student in one module presentation at a fixed cutoff date.

### Prediction point

Initial experiment: **day 40** after module presentation begins. Sensitivity experiments can compare days 20, 40, and 60.

### Outcome

- Adverse academic outcome: `Fail` or `Withdrawn`
- Successful academic outcome: `Pass` or `Distinction`

Train a probabilistic binary classifier for the adverse outcome. Convert its calibrated probability into dashboard support tiers:

- **Low support risk:** below a lower threshold
- **Medium support risk:** between lower and upper thresholds
- **High support risk:** at or above the upper threshold

Thresholds must be chosen only from training/validation data, with High-tier recall and faculty review capacity as explicit criteria. These tiers are decision-support priorities, not observed facts about students.

### Candidate prediction-time features

- Submitted-assessment count by cutoff
- Missing or late assessment count by cutoff
- Mean assessment score available by cutoff
- Weighted assessment score available by cutoff
- Total VLE clicks by cutoff
- Active VLE days by cutoff
- Recent 7-day and 14-day VLE activity
- Change in weekly engagement
- Days since last VLE activity
- Number of previous attempts
- Studied credits
- Module and presentation identifiers
- Highest education and age band, subject to ethical review

Demographic fields should be excluded from the first predictive model and retained separately for authorized fairness analysis.

## Secondary benchmark: UCI dataset 697

The UCI dataset contains 4,424 higher-education students and a three-class target: Dropout, Enrolled, and Graduate. It includes admission information and first- and second-semester curricular performance. It is useful for a simpler tabular benchmark but does not provide the same dated activity history as OULAD.

If used, report it as a separate experiment. Do not interpret its results as validation of the OULAD model.

## Kaggle datasets

Kaggle can be used as a distribution source or for an additional classroom demonstration, but dataset provenance must be checked. Prefer datasets with:

- a named original source;
- a clear licence;
- a data dictionary;
- non-synthetic records or explicit synthetic labelling;
- an independently observed target rather than a risk label calculated from the same input features.

Avoid using a dataset whose `risk_level` was generated directly from GPA, attendance, and assignment fields, because a model may merely reproduce the author's hidden rule. Avoid presenting synthetic data performance as evidence that the system will work at a university.

## Revised claim boundary

The project will demonstrate the technical and responsible-design feasibility of an early-warning decision-support prototype on public historical data. It will not claim local institutional validity, real intervention effectiveness, or deployment readiness.

