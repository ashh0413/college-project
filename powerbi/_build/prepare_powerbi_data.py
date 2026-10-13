import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "oulad"
OUT = Path(__file__).resolve().parent / "prepared_data.json"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value, integer=False):
    if value is None or value == "":
        return None
    try:
        return int(float(value)) if integer else float(value)
    except ValueError:
        return None


queue = read_csv(ART / "faculty_review_queue.csv")
integer_fields = {
    "id_student", "adverse_outcome", "num_of_prev_attempts", "studied_credits",
    "assessments_due", "assessments_submitted", "late_assessments", "total_clicks",
    "active_days", "clicks_last_7d", "clicks_previous_7d", "clicks_last_14d",
    "active_days_last_14d", "days_since_last_activity", "has_no_vle_activity",
}
float_fields = {
    "date_registration", "assessment_weight_submitted", "assessment_score_mean",
    "assessment_score_min", "weighted_assessment_score", "assessment_completion_rate",
    "assessment_weight_completion_rate", "click_trend_7d", "adverse_probability",
}
fact_headers = [
    "student_key", "id_student", "code_module", "code_presentation", "risk_tier",
    "risk_sort", "adverse_probability", "adverse_outcome", "final_result", "gender",
    "age_band", "disability", "highest_education", "imd_band", "num_of_prev_attempts",
    "studied_credits", "date_registration", "assessments_due", "assessments_submitted",
    "late_assessments", "assessment_weight_submitted", "assessment_score_mean",
    "assessment_score_min", "weighted_assessment_score", "assessment_completion_rate",
    "assessment_weight_completion_rate", "total_clicks", "active_days", "clicks_last_7d",
    "clicks_previous_7d", "clicks_last_14d", "active_days_last_14d",
    "days_since_last_activity", "click_trend_7d", "has_no_vle_activity",
    "presentation_season", "support_indicators", "faculty_review_options", "review_status",
]
risk_sort = {"Low": 1, "Medium": 2, "High": 3}
fact_rows = []
module_stats = defaultdict(lambda: [0, 0])
presentation_stats = defaultdict(lambda: [0, 0])
for raw in queue:
    row = dict(raw)
    for field in integer_fields:
        row[field] = number(row.get(field), integer=True)
    for field in float_fields:
        row[field] = number(row.get(field))
    row["student_key"] = f'{row["code_module"]}-{row["code_presentation"]}-{row["id_student"]}'
    row["risk_sort"] = risk_sort.get(row.get("risk_tier"))
    fact_rows.append([row.get(field) for field in fact_headers])
    module_stats[row["code_module"]][0] += 1
    module_stats[row["code_module"]][1] += row["adverse_outcome"] or 0
    presentation_stats[row["code_presentation"]][0] += 1
    presentation_stats[row["code_presentation"]][1] += row["adverse_outcome"] or 0


def typed_rows(path, integer_names=(), float_names=()):
    rows = read_csv(path)
    if not rows:
        return [], []
    headers = list(rows[0].keys())
    output = []
    for row in rows:
        for name in integer_names:
            row[name] = number(row.get(name), integer=True)
        for name in float_names:
            row[name] = number(row.get(name))
        output.append([row.get(name) for name in headers])
    return headers, output


risk_headers, risk_rows = typed_rows(
    ART / "risk_tier_summary.csv", {"rows"}, {"observed_adverse_rate", "mean_predicted_probability"}
)
risk_rows.sort(key=lambda row: risk_sort.get(row[0], 99))
model_headers, model_rows = typed_rows(
    ART / "model_comparison.csv", (),
    {"roc_auc", "average_precision", "brier_score", "log_loss", "high_risk_recall",
     "high_risk_precision", "high_review_rate", "high_threshold", "low_threshold"}
)
fair_headers, fair_rows = typed_rows(
    ART / "fairness_audit.csv", {"rows"},
    {"observed_adverse_rate", "high_selection_rate", "high_recall", "high_precision",
     "high_false_positive_rate", "elevated_selection_rate", "elevated_recall"}
)
shap_headers, shap_rows = typed_rows(
    ART / "explanations" / "shap_global.csv", (), {"mean_abs_shap", "mean_shap"}
)
shap_rows.sort(key=lambda row: row[1] or 0, reverse=True)
cal_headers, cal_rows = typed_rows(
    ART / "calibration_curve.csv", (), {"mean_predicted_probability", "observed_adverse_fraction"}
)

evaluation = json.loads((ART / "evaluation.json").read_text(encoding="utf-8"))
test = evaluation["test_metrics"]
metrics_rows = [
    ["Model", "Selected model", evaluation["selected_model"]],
    ["Data", "Training rows", evaluation["train_rows"]],
    ["Data", "Validation rows", evaluation["validation_rows"]],
    ["Data", "Test rows", evaluation["test_rows"]],
    ["Threshold", "Low threshold", evaluation["low_threshold"]],
    ["Threshold", "High threshold", evaluation["high_threshold"]],
    ["Test", "ROC-AUC", test["roc_auc"]],
    ["Test", "Average precision", test["average_precision"]],
    ["Test", "Brier score", test["brier_score"]],
    ["Test", "Log loss", test["log_loss"]],
    ["Test", "High-risk recall", test["high_risk_recall"]],
    ["Test", "High-risk precision", test["high_risk_precision"]],
    ["Test", "High-risk F1", test["high_risk_f1"]],
    ["Test", "High review rate", test["high_review_rate"]],
    ["Test", "Medium+High recall", test["elevated_risk_recall"]],
    ["Test", "Medium+High precision", test["elevated_risk_precision"]],
    ["Test", "Medium+High review rate", test["elevated_review_rate"]],
    ["Boundary", "Claim boundary", evaluation["claim_boundary"]],
]

dim_risk_rows = [
    ["Low", 1, "#16A34A", "Lower predicted need for review; continue normal monitoring."],
    ["Medium", 2, "#F59E0B", "Elevated predicted need; consider an academic check-in."],
    ["High", 3, "#DC2626", "Priority for faculty review; prediction is not a decision."],
]
dim_module_rows = [[k, v[0], v[1] / v[0] if v[0] else None] for k, v in sorted(module_stats.items())]
dim_presentation_rows = [[k, v[0], v[1] / v[0] if v[0] else None] for k, v in sorted(presentation_stats.items())]

dax_rows = [
    ["Total Records", "COUNTROWS(FactStudentRisk)", "Count of module-presentation student records."],
    ["Distinct Students", "DISTINCTCOUNT(FactStudentRisk[id_student])", "Unique student identifiers in the current filter context."],
    ["High Risk Records", 'CALCULATE([Total Records], DimRiskTier[risk_tier] = "High")', "Records marked High for faculty review."],
    ["Medium Risk Records", 'CALCULATE([Total Records], DimRiskTier[risk_tier] = "Medium")', "Records marked Medium."],
    ["Low Risk Records", 'CALCULATE([Total Records], DimRiskTier[risk_tier] = "Low")', "Records marked Low."],
    ["High Risk %", "DIVIDE([High Risk Records], [Total Records])", "Share of records in the High tier."],
    ["Observed Adverse Outcomes", "SUM(FactStudentRisk[adverse_outcome])", "Historical adverse outcomes; evaluation only."],
    ["Observed Adverse Rate", "DIVIDE([Observed Adverse Outcomes], [Total Records])", "Historical rate in the current filter context."],
    ["Average Risk Probability", "AVERAGE(FactStudentRisk[adverse_probability])", "Mean model probability; not certainty."],
    ["High Tier Recall", 'DIVIDE(CALCULATE([Observed Adverse Outcomes], DimRiskTier[risk_tier] = "High"), [Observed Adverse Outcomes])', "Priority metric: share of historical adverse outcomes captured in High."],
    ["Elevated Recall", 'DIVIDE(CALCULATE([Observed Adverse Outcomes], DimRiskTier[risk_tier] IN {"Medium", "High"}), [Observed Adverse Outcomes])', "Share captured in Medium or High."],
    ["High Tier Precision", 'DIVIDE(CALCULATE([Observed Adverse Outcomes], DimRiskTier[risk_tier] = "High"), [High Risk Records])', "Historical precision of the High tier."],
    ["Reviewed Records", 'CALCULATE([Total Records], FactStudentRisk[review_status] <> "Not reviewed")', "Records with a recorded faculty review state."],
    ["Review Completion %", "DIVIDE([Reviewed Records], [Total Records])", "Operational review progress."],
]

dashboard_rows = [
    [1, "Executive Overview", "Cards: Total Records, High Risk %, High Tier Recall, Elevated Recall", "Risk-tier bar; module adverse-rate bar", "Module, presentation, gender, age band", "Faculty monitoring overview"],
    [2, "Faculty Review Queue", "Cards: High Risk Records, Average Risk Probability", "Detailed table with probability, support indicators and review status", "Risk tier, module, presentation, review status", "Human review and support planning"],
    [3, "Model Evaluation", "Cards: ROC-AUC, Average Precision, High Recall, High Precision", "Model comparison; calibration; global SHAP factors", "Model", "Research evaluation only"],
    [4, "Fairness & Responsible Use", "Cards: group count and selection-rate range", "Group audit matrix for gender, age and disability", "Attribute, group", "Monitor disparities; never infer causality"],
    [5, "Student Support View", "Selected record only; no tier label required", "Attendance/engagement and assessment indicators with support suggestions", "Student key", "Supportive language; faculty-verified information"],
]

payload = {
    "fact": {"headers": fact_headers, "rows": fact_rows},
    "risk": {"headers": risk_headers, "rows": risk_rows},
    "model": {"headers": model_headers, "rows": model_rows},
    "fairness": {"headers": fair_headers, "rows": fair_rows},
    "shap": {"headers": shap_headers, "rows": shap_rows},
    "calibration": {"headers": cal_headers, "rows": cal_rows},
    "metrics": {"headers": ["category", "metric", "value"], "rows": metrics_rows},
    "dimRisk": {"headers": ["risk_tier", "risk_sort", "risk_color", "interpretation"], "rows": dim_risk_rows},
    "dimModule": {"headers": ["code_module", "record_count", "observed_adverse_rate"], "rows": dim_module_rows},
    "dimPresentation": {"headers": ["code_presentation", "record_count", "observed_adverse_rate"], "rows": dim_presentation_rows},
    "dax": {"headers": ["measure_name", "dax_expression", "purpose"], "rows": dax_rows},
    "dashboard": {"headers": ["page", "page_name", "kpis", "visuals", "slicers", "purpose"], "rows": dashboard_rows},
}
OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
print(f"Prepared {len(fact_rows)} fact rows at {OUT}")
