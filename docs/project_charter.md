# Project Charter

## Working title

**Student Success Analytics and Early Warning System**  
*A Machine Learning-Based Decision Support System for Early Academic Intervention*

## Purpose

The system will help authorized faculty identify patterns that may indicate a need for academic support. It will combine attendance, assessment, assignment, and previous-performance information to estimate a support-risk category. Faculty will review the evidence, speak with the student where appropriate, and remain responsible for the final response.

## Research question

How accurately and responsibly can routinely collected academic data identify students who may require early support, while maintaining explainability, fairness, privacy, and human oversight?

## Supporting questions

1. Which prediction-time academic indicators are most useful for identifying high-risk outcomes?
2. Which model provides the best balance of High-risk recall, precision, calibration, stability, and interpretability?
3. How do error rates differ across authorized demographic or programme groups?
4. Do SHAP explanations provide useful and understandable information to faculty?
5. Can transparent intervention rules translate model indicators into appropriate support options without automating decisions?

## Unit of analysis

For the public-data prototype, one row represents an OULAD student-module-presentation snapshot at a fixed cutoff date. Day 40 is the initial prediction point because it allows early support while providing some assessment and engagement evidence. Days 20 and 60 can be evaluated as sensitivity experiments.

## Proposed prediction target

The primary model predicts the probability of a later adverse academic outcome: `Fail` or `Withdrawn`, compared with `Pass` or `Distinction`. A calibrated probability is converted into three dashboard support tiers. The categories do not define a student's ability or personal circumstances.

- **High:** probability at or above a validation-selected upper threshold.
- **Medium:** probability between validation-selected lower and upper thresholds.
- **Low:** probability below the lower threshold.

Thresholds must be selected using training/validation data, prioritizing High-tier recall while considering review capacity. Test outcomes must not be used to tune thresholds.

## Minimum viable product

1. Approved, de-identified snapshot dataset.
2. Reproducible preprocessing pipeline.
3. Logistic Regression and tree-based model comparison.
4. Evaluation centred on High-risk recall and calibrated probabilities.
5. Global and student-level SHAP explanations.
6. Faculty dashboard with review status and intervention suggestions.
7. Student dashboard using supportive, non-alarming language.
8. Privacy, fairness, limitation, and model-card documentation.

## Out of scope for the MSc prototype

- Fully automated intervention or disciplinary action
- Mental-health diagnosis or inference
- Continuous surveillance of students
- Use of private communications or unrelated personal data
- Claims that predictions or interventions cause improved outcomes
- Claims of local institutional validity or production deployment without fresh local validation

## Acceptance criteria

- No end-of-term information enters prediction-time features.
- Performance is reported per class, with High-risk recall clearly highlighted.
- Results include confusion matrices, calibration evidence, and subgroup error analysis where permitted.
- Explanations are presented as model contributions rather than causes.
- Every displayed prediction includes its date, model version, and human-review status.
- No action is executed directly from a risk score.
