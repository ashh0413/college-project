# Student Success Analytics — Power BI Build Guide

This dashboard supports faculty review and early academic intervention. It must not be used to make automatic or punitive decisions about students.

## 1. Load the workbook

1. Open Power BI Desktop.
2. Select **Get data → Excel workbook**.
3. Choose `Student_Success_PowerBI_Data_Model.xlsx`.
4. Load these tables: `FactStudentRisk`, `DimRiskTier`, `DimModule`, `DimPresentation`, `ModelMetrics`, `ModelComparison`, `FairnessAudit`, `SHAPFactors`, `Calibration`, `DAXMeasures`, and `DashboardSpec`.
5. Import `student_success_theme.json` using **View → Themes → Browse for themes**.

## 2. Create the model

Create single-direction, one-to-many relationships:

- `DimRiskTier[risk_tier]` → `FactStudentRisk[risk_tier]`
- `DimModule[code_module]` → `FactStudentRisk[code_module]`
- `DimPresentation[code_presentation]` → `FactStudentRisk[code_presentation]`

Sort `DimRiskTier[risk_tier]` by `DimRiskTier[risk_sort]`. Hide technical fields such as `risk_sort` from report view.

## 3. Add the measures

Create the measures listed in the workbook's **DAX Measures** sheet. Important measures are:

```DAX
Total Records = COUNTROWS(FactStudentRisk)

Distinct Students = DISTINCTCOUNT(FactStudentRisk[id_student])

High Risk Records =
CALCULATE([Total Records], DimRiskTier[risk_tier] = "High")

High Risk % = DIVIDE([High Risk Records], [Total Records])

Observed Adverse Outcomes = SUM(FactStudentRisk[adverse_outcome])

Observed Adverse Rate =
DIVIDE([Observed Adverse Outcomes], [Total Records])

Average Risk Probability = AVERAGE(FactStudentRisk[adverse_probability])

High Tier Recall =
DIVIDE(
    CALCULATE([Observed Adverse Outcomes], DimRiskTier[risk_tier] = "High"),
    [Observed Adverse Outcomes]
)

Elevated Recall =
DIVIDE(
    CALCULATE(
        [Observed Adverse Outcomes],
        DimRiskTier[risk_tier] IN {"Medium", "High"}
    ),
    [Observed Adverse Outcomes]
)

High Tier Precision =
DIVIDE(
    CALCULATE([Observed Adverse Outcomes], DimRiskTier[risk_tier] = "High"),
    [High Risk Records]
)

Reviewed Records =
CALCULATE(
    [Total Records],
    FactStudentRisk[review_status] <> "Not reviewed"
)

Review Completion % = DIVIDE([Reviewed Records], [Total Records])
```

Format probabilities, rates, recall and precision as percentages with one decimal place.

## 4. Build the report pages

### Page 1 — Executive Overview

- KPI cards: Total Records, High Risk %, High Tier Recall, Elevated Recall, Observed Adverse Rate.
- Clustered bar chart: records by risk tier. Apply the tier colours: Low `#16A34A`, Medium `#F59E0B`, High `#DC2626`.
- Bar chart: Observed Adverse Rate by module.
- Slicers: module, presentation, gender and age band.
- Add this note: *Predictions prioritize human review; they are not facts or automated decisions.*

### Page 2 — Faculty Review Queue

- Slicers: risk tier, module, presentation and review status.
- Table columns: student key, module, presentation, risk tier, probability, assessment completion, weighted assessment score, clicks in last 14 days, days since last activity, support indicators, faculty review options and review status.
- Apply conditional formatting only to risk tier and probability. Do not use red formatting for personal characteristics.
- Default the page filter to High and Medium, while allowing faculty to view all records.

### Page 3 — Model Evaluation

- KPI cards: ROC-AUC, Average Precision, High-tier Recall and High-tier Precision from `ModelMetrics`.
- Matrix: `ModelComparison` metrics by model.
- Line chart: mean predicted probability against observed adverse fraction from `Calibration`; add a reference line where observed equals predicted if desired.
- Bar chart: top 15 `SHAPFactors[mean_abs_shap]` by feature.
- State that SHAP explains model contribution, not causation.

### Page 4 — Fairness and Responsible Use

- Matrix using attribute, group, rows, observed adverse rate, High selection rate, High recall, High precision and High false-positive rate.
- Slicers: attribute and group.
- Use differences as monitoring signals. Small groups should be interpreted cautiously.
- Do not rank protected groups or use protected attributes to justify adverse treatment.

### Page 5 — Student Support View

- Use a single-select student key slicer.
- Show assessment completion, score, recent engagement and days since last activity.
- Show supportive suggestions only after faculty verification.
- Avoid displaying comparative rank, certainty language or a punitive label to students.

## 5. Validate before demonstration

- Test slicer interactions and drill-through.
- Confirm High-tier recall remains the priority model metric.
- Check that hidden fields and sensitive attributes are not exposed to unauthorized viewers.
- Add row-level security before using institutional data.
- Present all results as evaluation on historical public OULAD data, not evidence of local deployment effectiveness.
