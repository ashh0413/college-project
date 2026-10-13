# Model Card: OULAD Day-40 Early-Warning Prototype

## Model details

- Version: 0.1 research prototype
- Model family: Calibrated Random Forest
- Prediction point: Day 40
- Output: Probability of later `Fail` or `Withdrawn`
- Training presentations: 2013B and 2013J
- Validation presentation: 2014B
- Test presentation: 2014J

## Intended use

Prioritize records for authorized faculty review and supportive outreach in a research demonstration.

## Prohibited use

- Automated decisions
- Discipline, grading, enrolment restriction, or denial of services
- Mental-health, motivation, or character inference
- Use at another institution without new validation
- Use as the only basis for contacting or classifying a student

## Test performance

- ROC-AUC: 0.761
- Precision-recall AUC: 0.711
- Brier score: 0.193
- High-tier recall: 45.5%
- High-tier precision: 72.5%
- High-tier review rate: 24.9%
- Medium-plus-High recall: 74.5%

## Threshold policy

Thresholds were selected on validation data under assumed review limits of 30% for High and 60% for Medium-plus-High. These are research assumptions, not institutional policy.

## Data exclusions

Sensitive/audit fields and student identifiers are not predictive inputs. Final results and unregistration dates are excluded to prevent outcome leakage.

## Explainability

Permutation SHAP explains the calibrated probability for a stratified test sample. SHAP values are model explanations, not causal explanations.

## Important risks

- Missed students: High-tier recall is below 50%.
- False alerts: 619 non-adverse test records entered High.
- Portability: module and platform patterns may not generalize.
- Unequal error patterns: subgroup differences require investigation.
- Behavioural misinterpretation: VLE activity does not represent all study activity.

## Human oversight

Faculty must verify records, consider student context, choose proportionate support, and document the review. The student should have a route to correct inaccurate data.

