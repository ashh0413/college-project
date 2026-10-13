# Student Success Analytics and Early Warning System

## A Machine Learning-Based Decision Support System for Early Academic Intervention

## Abstract

This project develops and evaluates a research prototype for identifying students who may benefit from early academic support. It uses the anonymized Open University Learning Analytics Dataset (OULAD) and constructs a day-40 snapshot from assessment, registration, previous-attempt, and Virtual Learning Environment activity records. The model estimates the probability of a later adverse academic outcome, defined as `Fail` or `Withdrawn`, while `Pass` and `Distinction` form the comparison class.

Four models were evaluated using chronological cohorts. Random Forest was selected on 2014B validation data and evaluated once on the untouched 2014J test cohort. On that test cohort, the model achieved ROC-AUC 0.761 and precision-recall AUC 0.711. Under a validation-selected review-capacity policy, the High tier contained 24.9% of test records and identified 45.5% of later adverse outcomes, with 72.5% precision. Medium and High together identified 74.5% of later adverse outcomes while containing 53.5% of records.

The prototype includes model-agnostic SHAP explanations, transparent intervention rules, subgroup auditing, and separate faculty and student dashboards. Predictions are presented as uncertain indicators rather than facts. The system does not automate academic decisions, and the public-data results do not establish effectiveness at another institution.

## 1. Introduction

Educational institutions record assessments, assignment submissions, course engagement, previous academic attempts, and final outcomes. These records can help faculty notice students who may require support, but reviewing many records manually is difficult. An early-warning system can organize available information and prioritize cases for human review.

This project treats early warning as decision support. It does not determine a student's ability, intention, or personal circumstances. Faculty members remain responsible for checking the evidence, speaking with the student where appropriate, and selecting any supportive response.

## 2. Problem Statement

Academic difficulties may be recognized only after a failed assessment, withdrawal, or final result. A reproducible method is needed to summarize early academic indicators, estimate the probability of a later adverse outcome, explain the model estimate, and help faculty prioritize supportive review without automating decisions.

## 3. Motivation

Earlier support may provide more time for tutoring, study planning, assessment guidance, access assistance, or an academic-advisor conversation. However, an inaccurate or poorly governed model can stigmatize students or direct attention unevenly. The project therefore combines predictive performance with calibration, explainability, subgroup evaluation, privacy controls, and human oversight.

## 4. Main Objective

To design and evaluate a machine learning-based decision-support prototype that uses information available by day 40 of a module presentation to identify students who may benefit from academic support.

## 5. Specific Objectives

1. Integrate the relational OULAD tables into one leakage-aware day-40 snapshot.
2. Define an observable later academic outcome without presenting it as a diagnosis.
3. Compare an uninformed baseline, Logistic Regression, Random Forest, and gradient boosting.
4. Select the model and probability thresholds using validation data only.
5. Prioritize recall within a declared faculty-review capacity.
6. Evaluate discrimination, precision, recall, calibration, and subgroup error patterns.
7. Explain model behaviour using SHAP.
8. Translate observable indicators into transparent support options.
9. Provide separate faculty, student, and research-evaluation dashboard views.
10. Document privacy, ethics, limitations, and responsible-use boundaries.

## 6. Proposed Solution

The solution contains five layers:

1. A reproducible OULAD data-integration and feature-engineering pipeline
2. A calibrated binary classifier for later `Fail` or `Withdrawn`
3. Validation-selected Low, Medium, and High support tiers
4. SHAP explanations and rule-based intervention options
5. Streamlit dashboards designed for faculty review and student support

The tier is a review priority. It is not a disciplinary label and does not execute an action.

## 7. Dataset and Features

OULAD is an anonymized higher-education learning-analytics dataset released by The Open University. The downloaded release contains linked CSV tables for students, registrations, assessments, submissions, courses, VLE resources, and dated VLE interactions.

The raw `studentInfo` table contains 32,593 student-module-presentation records. After applying the day-40 cohort rules, the modelling snapshot contains 27,042 records and 37 columns.

### Prediction-time features

- Previous module attempts
- Studied credits
- Registration timing
- Assessments due and submitted by day 40
- Late assessment count
- Available assessment scores and weights
- Assessment completion rates
- Total and recent VLE clicks
- Active VLE days
- Days since last VLE activity
- Seven-day activity change
- Module and presentation season

VLE activity is not described as classroom attendance. OULAD does not provide GPA or conventional backlog fields, so these were not fabricated.

### Excluded fields

The model excludes student identifiers, final results, unregistration dates, and demographic/audit attributes. Gender, age band, disability, highest education, and deprivation band remain outside the predictive feature set.

## 8. Data Science Methodology

The work follows a CRISP-DM-style process: problem understanding, data understanding, data preparation, modelling, evaluation, explanation, and prototype delivery.

### Snapshot construction

One row represents one student in one module presentation at day 40. Students must have registered by the cutoff. Students whose withdrawal was already recorded by day 40 are excluded because their outcome was already known. Later withdrawals remain valid outcomes.

Assessments contribute only when their due date is on or before day 40 and the recorded submission is available by day 40. VLE events are filtered to the cutoff before aggregation.

### Chronological evaluation

- Training: 2013B and 2013J — 11,628 records
- Validation: 2014B — 6,366 records
- Test: 2014J — 9,048 records

This design provides a more realistic later-cohort test than a random row split. The test cohort was not used for model or threshold selection.

### Missing values

Numeric missing values are imputed using training-fold medians. Missingness indicators are created within the pipeline. Categorical values use the most frequent training value, and unseen categories are ignored safely by one-hot encoding.

## 9. Models Compared

- Dummy prior-probability classifier
- Balanced Logistic Regression
- Balanced Random Forest
- Balanced Histogram Gradient Boosting

The non-dummy models were probability-calibrated using grouped cross-validation across training presentations. Random Forest was selected because it produced the highest validation High-tier recall, followed by validation precision-recall AUC and Brier score as tie-breakers.

Logistic Regression performed almost identically. This should be discussed as a practical interpretability-versus-complexity decision rather than evidence that Random Forest is universally superior.

## 10. Evaluation Metrics

The evaluation includes:

- High-tier recall, precision, F1, and review rate
- Medium-plus-High recall, precision, and review rate
- ROC-AUC
- Precision-recall AUC
- Brier score
- Log loss
- Confusion matrix
- Reliability/calibration curve
- Subgroup selection, recall, precision, and false-positive rates

### Untouched test results

| Metric | Result |
|---|---:|
| ROC-AUC | 0.761 |
| Precision-recall AUC | 0.711 |
| Brier score | 0.193 |
| Log loss | 0.570 |
| High-tier recall | 45.5% |
| High-tier precision | 72.5% |
| High-tier F1 | 55.9% |
| High-tier review rate | 24.9% |
| Medium-plus-High recall | 74.5% |
| Medium-plus-High precision | 55.4% |
| Medium-plus-High review rate | 53.5% |

The High-tier confusion matrix is `[[4836, 619], [1959, 1634]]`, ordered as actual non-adverse and adverse outcomes. The 1,959 missed adverse outcomes show why the model must not be treated as a complete identification system.

## 11. Risk Tiers and Thresholds

The validation process imposed two assumed capacity limits:

- High review queue: at most 30% of validation records
- Medium-plus-High queue: at most 60% of validation records

The selected validation thresholds were:

- Low/Medium threshold: 0.3882
- Medium/High threshold: 0.5915

On the test set:

| Tier | Records | Observed adverse rate | Mean predicted probability |
|---|---:|---:|---:|
| Low | 4,210 | 21.7% | 26.0% |
| Medium | 2,585 | 40.4% | 49.8% |
| High | 2,253 | 72.5% | 69.3% |

The capacity limits are research assumptions. A real institution must replace them with locally approved review capacity and consequences.

## 12. Explainable AI Using SHAP

Model-agnostic permutation SHAP was calculated for a stratified sample of 75 test records using 25 background records. The output explained is the calibrated probability of later `Fail` or `Withdrawn`.

The leading global contributors in the explained sample were:

1. Mean assessment score
2. Minimum assessment score
3. Weighted assessment score
4. Module context
5. VLE clicks during the previous 14 days
6. Active VLE days during the previous 14 days

SHAP explains the model calculation, not the student's circumstances and not the cause of an academic outcome. Module context may reflect differences in assessment design, student mix, or course structure rather than a property of an individual student.

## 13. Recommendation and Intervention System

The recommendation layer uses visible, deterministic rules rather than an unrestricted generative model. Possible indicators and support options include:

| Indicator | Faculty-reviewed option |
|---|---|
| No recent VLE activity | Check access, study planning, and module engagement |
| Incomplete due assessment | Review the record and discuss deadline or academic support |
| Low available assessment score | Offer feedback, tutoring, or study-skills resources |
| Recent engagement decline | Verify the pattern and consider a supportive check-in |
| Previous module attempt | Consider an academic-advisor review |

The options do not automatically send messages, change grades, restrict enrolment, or create disciplinary actions.

## 14. Faculty and Student Dashboards

### Faculty view

- High/Medium/Low filtering
- Module filtering
- Ranked review queue
- Estimated probability and support tier
- Indicators to verify
- Faculty-reviewed support options
- SHAP explanation for sampled records
- Persistent human-review warning

### Student view

- Assessment completion
- Available assessment average
- Active VLE days and recent activity
- Support resources and correction guidance

The Student view intentionally omits the model risk tier and probability. This reduces stigma and focuses the interface on understandable learning records and support.

### Evaluation view

- Untouched test metrics
- Validation model comparison
- Risk-tier profile
- Subgroup audit tables
- Global SHAP factors

## 15. Technology Stack

- Python 3.12
- Pandas and NumPy
- Scikit-learn
- SHAP
- Plotly
- Streamlit
- Joblib
- Pytest
- Git-compatible repository layout

## 16. System Workflow

```text
Official anonymized OULAD CSV files
              ↓
Day-40 filtering and relational integration
              ↓
Leakage checks and feature engineering
              ↓
Chronological train / validation / test cohorts
              ↓
Calibrated model comparison
              ↓
Validation-selected review thresholds
              ↓
Untouched test evaluation and subgroup audit
              ↓
SHAP explanations and transparent support options
              ↓
Faculty review / student-support dashboard
              ↓
Human decision and documented follow-up
```

## 17. Expected and Achieved Outcomes

The project produced:

- A reproducible day-40 OULAD snapshot
- EDA and data-quality artifacts
- Four-model comparison
- A calibrated Random Forest model bundle
- Validation-selected support tiers
- Untouched later-cohort test evaluation
- SHAP global and sampled local explanations
- A subgroup audit
- A 9,048-record demonstration review queue
- Separate Faculty, Student, and Evaluation dashboards
- Automated tests and complete run scripts
- Ethics, limitations, and model documentation

No claim is made that the prototype improves student outcomes. That would require a prospective intervention study.

## 18. Privacy and Ethical Considerations

- Use the minimum necessary data.
- Keep direct identifiers out of model-development data.
- Restrict access to student-level outputs.
- Record the model version, prediction date, reviewer, and response.
- Establish retention and deletion periods.
- Allow corrections to inaccurate source information.
- Prevent disciplinary or automatic administrative use.
- Review subgroup errors before any local pilot.
- Communicate uncertainty and the right to human review.
- Do not infer mental health, motivation, or personal circumstances from platform activity.

OULAD is already anonymized, but public-data status does not remove the obligation to report results responsibly.

## 19. Subgroup Audit

On the test cohort, High-tier recall ranges observed in groups meeting the minimum sample-size rule were:

- Gender: 45.4%–45.6%
- Age band: 40.4%–47.6%
- Disability indicator: 45.0%–49.0%
- Highest education: 35.5%–48.4%

The gender false-positive rate ranged from 8.0% to 15.7%, a difference requiring investigation. These descriptive differences do not independently prove fairness or unfairness. Group composition, outcome prevalence, sample size, and institutional context must be examined before conclusions are drawn.

## 20. Limitations

- OULAD describes distance-learning modules at one institution.
- VLE activity omits offline study and is not attendance.
- The model cannot observe personal circumstances or all forms of engagement.
- The outcome groups Fail and Withdrawn even though they may have different causes.
- Module context is predictive but may reduce portability.
- Random Forest only narrowly outperformed Logistic Regression during validation.
- High-tier recall is 45.5%, leaving many later adverse outcomes outside High.
- Tier thresholds reflect assumed capacity rather than a real institution's workflow.
- SHAP explanations are not causal explanations.
- The subgroup audit is descriptive and limited by available attributes.
- The dashboard is a research prototype without production authentication or audit logging.
- Public-data performance does not establish local validity.

## 21. Future Scope

- Compare day-20, day-40, and day-60 snapshots.
- Separate withdrawal and failure models.
- Evaluate Logistic Regression as a simpler deployment candidate.
- Conduct module-specific and cross-module validation.
- Add uncertainty and data-quality warnings to every student record.
- Perform prospective local validation with institutional approval.
- Co-design explanations and support workflows with students and faculty.
- Add authenticated role-based access, audit logs, retention controls, and correction workflows.
- Evaluate whether interventions are timely, acceptable, and beneficial using an ethically approved study.

## 22. Realistic Development Timeline

| Phase | Weeks |
|---|---:|
| Literature review and research design | 1–2 |
| Dataset study and ethical scope | 3 |
| Relational integration and data quality | 4–5 |
| EDA and feature engineering | 6–7 |
| Baselines and model comparison | 8–9 |
| Calibration, thresholds, and test evaluation | 10 |
| SHAP and subgroup audit | 11 |
| Intervention rules and dashboards | 12–13 |
| Testing and sensitivity analysis | 14 |
| Dissertation writing | 15 |
| Presentation and final demonstration | 16 |

## 23. Conclusion

The project demonstrates a complete and responsible early-warning research workflow on anonymized public higher-education data. The selected model provides useful ranking information but is incomplete and fallible. Its appropriate role is to help authorized faculty organize supportive review, not to replace professional judgement or make decisions about students.

## References

1. Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics Dataset. *Scientific Data, 4*, 170171. https://doi.org/10.1038/sdata.2017.171
2. Lundberg, S. M., & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. *Advances in Neural Information Processing Systems, 30*.
3. Scikit-learn documentation. https://scikit-learn.org/
4. SHAP documentation. https://shap.readthedocs.io/

