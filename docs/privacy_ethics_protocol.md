# Privacy and Ethics Protocol

## Purpose limitation

Use model outputs only to offer academic support. Do not reuse them for discipline, grading, admissions, scholarships, immigration, surveillance, or unrelated profiling.

## Data minimization

Collect only fields needed for the approved prediction point and evaluation. Keep direct identifiers and free-text notes outside the modelling dataset.

## Access control

- Faculty: assigned students and review workflow
- Students: their own learning records and support information
- Researchers: de-identified analytical data
- Administrators: aggregate monitoring unless student-level access is explicitly required

## Human review procedure

1. Confirm the prediction date and model version.
2. Check that source records are complete and correct.
3. Review the SHAP factors as model contributions, not causes.
4. Consider information the system cannot observe.
5. Select a supportive and proportionate response, or take no action.
6. Record the review outcome.
7. Provide a correction or escalation path.

## Student communication

Communication should explain that analytics provide an uncertain indicator based on available academic records. Avoid deterministic statements such as “you will fail.” State the available support and how incorrect data can be corrected.

## Fairness review

Measure subgroup sample size, outcome prevalence, selection rate, recall, precision, and false-positive rate. Investigate differences with domain experts and affected groups. Do not treat one numerical parity measure as complete proof of fairness.

## Security and retention

- Encrypt data in transit and at rest.
- Use role-based access and access logs.
- Separate re-identification keys from analytical records.
- Define retention and deletion dates before collection.
- Remove obsolete predictions and review notes according to policy.
- Test backup, recovery, and breach-response procedures.

## Deployment gate

The prototype must not be deployed on local student records until institutional approval, data-protection review, local validation, security testing, user testing, and operational ownership are complete.

