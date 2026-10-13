import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const buildDir = path.dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(await fs.readFile(path.join(buildDir, "prepared_data.json"), "utf8"));
const outputDir = path.resolve(buildDir, "..", "..", "outputs", "01a00aa7-8f08-70c0-b41a-6a4f77261739");
const previewDir = path.join(buildDir, "previews");
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const wb = Workbook.create();
const navy = "#17324D";
const blue = "#2563EB";
const pale = "#EAF2FF";
const border = "#D7E0EA";
const dark = "#1F2937";

function colName(index) {
  let name = "";
  let n = index + 1;
  while (n > 0) {
    const remainder = (n - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function styleHeader(range) {
  range.format.fill = navy;
  range.format.font = { bold: true, color: "#FFFFFF" };
  range.format.wrapText = true;
  range.format.rowHeight = 28;
  range.format.borders = { preset: "all", style: "thin", color: border };
}

function addTableSheet(name, payload, tableName, widths = {}) {
  const sheet = wb.worksheets.add(name);
  sheet.showGridLines = false;
  const matrix = [payload.headers, ...payload.rows];
  const endCol = colName(payload.headers.length - 1);
  const endRow = matrix.length;
  sheet.getRange(`A1:${endCol}${endRow}`).values = matrix;
  styleHeader(sheet.getRange(`A1:${endCol}1`));
  sheet.getRange(`A1:${endCol}${endRow}`).format.borders = { preset: "inside", style: "thin", color: "#EDF1F5" };
  sheet.freezePanes.freezeRows(1);
  sheet.tables.add(`A1:${endCol}${endRow}`, true, tableName);
  for (let i = 0; i < payload.headers.length; i++) {
    const header = payload.headers[i];
    const width = widths[header] ?? Math.min(Math.max(header.length + 3, 12), 24);
    sheet.getRange(`${colName(i)}:${colName(i)}`).format.columnWidth = width;
  }
  return sheet;
}

const readme = wb.worksheets.add("README");
readme.showGridLines = false;
readme.getRange("A1:H2").merge();
readme.getRange("A1").values = [["Student Success Analytics — Power BI Data Model"]];
readme.getRange("A1:H2").format.fill = navy;
readme.getRange("A1:H2").format.font = { bold: true, color: "#FFFFFF", size: 20 };
readme.getRange("A1:H2").format.verticalAlignment = "center";
readme.getRange("A4:H4").merge();
readme.getRange("A4").values = [["Purpose: help faculty identify students who may benefit from academic support. Predictions are decision-support signals, not facts or automated decisions."]];
readme.getRange("A4:H4").format.fill = pale;
readme.getRange("A4:H4").format.font = { color: dark, italic: true };
readme.getRange("A4:H4").format.wrapText = true;
readme.getRange("A6:B13").values = [
  ["Power BI table", "Role"],
  ["FactStudentRisk", "Main prediction and student-support fact table"],
  ["DimRiskTier", "Low / Medium / High labels, sort order and colours"],
  ["DimModule", "Module slicer and summary dimension"],
  ["DimPresentation", "Presentation slicer and summary dimension"],
  ["ModelMetrics", "Held-out test metrics and claim boundary"],
  ["FairnessAudit", "Group-level monitoring indicators"],
  ["SHAPFactors", "Global feature contribution summary"],
];
styleHeader(readme.getRange("A6:B6"));
readme.getRange("D6:H6").merge();
readme.getRange("D6").values = [["Recommended relationships"]];
styleHeader(readme.getRange("D6:H6"));
readme.getRange("D7:H11").merge(true);
readme.getRange("D7:H11").values = [
  ["DimRiskTier[risk_tier] 1 → * FactStudentRisk[risk_tier]"],
  ["DimModule[code_module] 1 → * FactStudentRisk[code_module]"],
  ["DimPresentation[code_presentation] 1 → * FactStudentRisk[code_presentation]"],
  ["Set DimRiskTier[risk_tier] to sort by DimRiskTier[risk_sort]."],
  ["Use single-direction filtering from dimensions to the fact table."],
];
readme.getRange("A15:H15").merge();
readme.getRange("A15").values = [["Responsible-use rules"]];
styleHeader(readme.getRange("A15:H15"));
readme.getRange("A16:H20").merge(true);
readme.getRange("A16:H20").values = [
  ["1. Faculty must review contextual information before any intervention."],
  ["2. Use supportive, non-punitive interventions and record the review outcome."],
  ["3. Limit access, avoid exposing sensitive attributes, and retain data only as required."],
  ["4. Monitor recall, false positives and group disparities after every data/model update."],
  ["5. Public OULAD findings show historical association only; they do not prove causality or local effectiveness."],
];
readme.getRange("A1:H20").format.wrapText = true;
readme.getRange("A:A").format.columnWidth = 28;
readme.getRange("B:B").format.columnWidth = 44;
for (const c of ["D","E","F","G","H"]) readme.getRange(`${c}:${c}`).format.columnWidth = 18;
readme.getRange("4:4").format.rowHeight = 42;
readme.getRange("16:20").format.rowHeight = 28;

const preview = wb.worksheets.add("PowerBI Preview");
preview.showGridLines = false;
preview.getRange("A1:M2").merge();
preview.getRange("A1").values = [["Student Success Analytics — Executive Overview"]];
preview.getRange("A1:M2").format.fill = navy;
preview.getRange("A1:M2").format.font = { bold: true, color: "#FFFFFF", size: 20 };
preview.getRange("A3:M3").merge();
preview.getRange("A3").values = [["Faculty decision support • held-out OULAD test records • human review required"]];
preview.getRange("A3:M3").format.fill = pale;
preview.getRange("A3:M3").format.font = { color: dark, italic: true };
preview.getRange("A5:B7").values = [["Total records", null],["High risk %", null],["High-tier recall", null]];
preview.getRange("D5:E7").values = [["Observed adverse rate", null],["Average risk probability", null],["Medium+High recall", null]];
preview.getRange("B5:B7").formulas = [["=COUNTA(FactStudentRisk!$A$2:$A$9049)"],["=COUNTIF(FactStudentRisk!$E$2:$E$9049,\"High\")/COUNTA(FactStudentRisk!$A$2:$A$9049)"],["=COUNTIFS(FactStudentRisk!$E$2:$E$9049,\"High\",FactStudentRisk!$H$2:$H$9049,1)/SUM(FactStudentRisk!$H$2:$H$9049)"]];
preview.getRange("E5:E7").formulas = [["=AVERAGE(FactStudentRisk!$H$2:$H$9049)"],["=AVERAGE(FactStudentRisk!$G$2:$G$9049)"],["=(COUNTIFS(FactStudentRisk!$E$2:$E$9049,\"Medium\",FactStudentRisk!$H$2:$H$9049,1)+COUNTIFS(FactStudentRisk!$E$2:$E$9049,\"High\",FactStudentRisk!$H$2:$H$9049,1))/SUM(FactStudentRisk!$H$2:$H$9049)"]];
for (const r of ["A5:B7","D5:E7"]) {
  preview.getRange(r).format.fill = "#F8FAFC";
  preview.getRange(r).format.borders = { preset: "all", style: "thin", color: border };
}
preview.getRange("A5:A7").format.font = { bold: true, color: dark };
preview.getRange("D5:D7").format.font = { bold: true, color: dark };
preview.getRange("B5").format.numberFormat = "#,##0";
preview.getRange("B6:B7").format.numberFormat = "0.0%";
preview.getRange("E5:E7").format.numberFormat = "0.0%";
preview.getRange("A10:D13").values = [["Risk tier","Records","Observed adverse rate","Mean predicted probability"],[null,null,null,null],[null,null,null,null],[null,null,null,null]];
preview.getRange("A11:D13").formulas = [
  ["=RiskSummary!A2","=RiskSummary!B2","=RiskSummary!C2","=RiskSummary!D2"],
  ["=RiskSummary!A3","=RiskSummary!B3","=RiskSummary!C3","=RiskSummary!D3"],
  ["=RiskSummary!A4","=RiskSummary!B4","=RiskSummary!C4","=RiskSummary!D4"],
];
styleHeader(preview.getRange("A10:D10"));
preview.getRange("C11:D13").format.numberFormat = "0.0%";
preview.getRange("A17:C24").values = [["Module","Records","Observed adverse rate"], ...Array(7).fill([null,null,null])];
preview.getRange("D17:E24").values = [["Module","Observed adverse rate"], ...Array(7).fill([null,null])];
for (let i = 0; i < 7; i++) {
  const row = 18 + i;
  const source = 2 + i;
  preview.getRange(`A${row}:C${row}`).formulas = [[`=DimModule!A${source}`,`=DimModule!B${source}`,`=DimModule!C${source}`]];
  preview.getRange(`D${row}:E${row}`).formulas = [[`=DimModule!A${source}`,`=DimModule!C${source}`]];
}
styleHeader(preview.getRange("A17:C17"));
styleHeader(preview.getRange("D17:E17"));
preview.getRange("C18:C24").format.numberFormat = "0.0%";
preview.getRange("E18:E24").format.numberFormat = "0.0%";
const riskChart = preview.charts.add("bar", preview.getRange("A10:B13"));
riskChart.title = "Records by risk tier";
riskChart.hasLegend = false;
riskChart.setPosition("F5", "M15");
const moduleChart = preview.charts.add("bar", preview.getRange("D17:E24"));
moduleChart.title = "Historical adverse rate by module";
moduleChart.hasLegend = false;
moduleChart.yAxis = { numberFormatCode: "0%" };
moduleChart.setPosition("F17", "M31");
preview.getRange("A27:M29").merge();
preview.getRange("A27").values = [["Interpretation: use the High tier to prioritize review, while Medium+High recall shows broader coverage. The dashboard does not determine student outcomes or mandate interventions."]];
preview.getRange("A27:M29").format.fill = "#FFF7ED";
preview.getRange("A27:M29").format.font = { color: "#9A3412", italic: true };
preview.getRange("A27:M29").format.wrapText = true;
preview.getRange("A:M").format.columnWidth = 14;
preview.getRange("A:A").format.columnWidth = 24;
preview.getRange("D:D").format.columnWidth = 27;

const fact = addTableSheet("FactStudentRisk", data.fact, "FactStudentRisk", {
  student_key: 28, support_indicators: 48, faculty_review_options: 52, review_status: 18,
  highest_education: 25, adverse_probability: 20, code_presentation: 20,
});
fact.getRange("G2:G9049").format.numberFormat = "0.000";
fact.getRange("Y2:Z9049").format.numberFormat = "0.0%";
fact.getRange("E2:E9049").conditionalFormats.add("containsText", { text: "High", format: { fill: "#FEE2E2", font: { color: "#991B1B", bold: true } } });
fact.getRange("E2:E9049").conditionalFormats.add("containsText", { text: "Medium", format: { fill: "#FEF3C7", font: { color: "#92400E" } } });
fact.getRange("E2:E9049").conditionalFormats.add("containsText", { text: "Low", format: { fill: "#DCFCE7", font: { color: "#166534" } } });

addTableSheet("DimRiskTier", data.dimRisk, "DimRiskTier", { interpretation: 65, risk_color: 16 });
addTableSheet("DimModule", data.dimModule, "DimModule", { code_module: 18, observed_adverse_rate: 24 }).getRange("C2:C8").format.numberFormat = "0.0%";
addTableSheet("DimPresentation", data.dimPresentation, "DimPresentation", { code_presentation: 22, observed_adverse_rate: 24 }).getRange("C2:C20").format.numberFormat = "0.0%";
addTableSheet("RiskSummary", data.risk, "RiskSummary", { observed_adverse_rate: 24, mean_predicted_probability: 28 }).getRange("C2:D10").format.numberFormat = "0.0%";
addTableSheet("ModelMetrics", data.metrics, "ModelMetrics", { category: 16, metric: 28, value: 65 });
addTableSheet("ModelComparison", data.model, "ModelComparison", { model: 26 }).getRange("B2:J10").format.numberFormat = "0.000";
addTableSheet("FairnessAudit", data.fairness, "FairnessAudit", { attribute: 18, group: 28 }).getRange("D2:J100").format.numberFormat = "0.0%";
addTableSheet("SHAPFactors", data.shap, "SHAPFactors", { feature: 36, mean_abs_shap: 20, mean_shap: 18 }).getRange("B2:C100").format.numberFormat = "0.0000";
addTableSheet("Calibration", data.calibration, "Calibration", { mean_predicted_probability: 30, observed_adverse_fraction: 30 }).getRange("A2:B100").format.numberFormat = "0.0%";
addTableSheet("DAX Measures", data.dax, "DAXMeasures", { measure_name: 28, dax_expression: 90, purpose: 52 });
addTableSheet("Dashboard Spec", data.dashboard, "DashboardSpec", { page: 10, page_name: 28, kpis: 55, visuals: 65, slicers: 38, purpose: 48 });

const inspect = await wb.inspect({ kind: "sheet,table", maxChars: 8000, tableMaxRows: 3, tableMaxCols: 8 });
await fs.writeFile(path.join(buildDir, "inspection.txt"), inspect.ndjson ?? String(inspect), "utf8");
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, maxChars: 8000 });
await fs.writeFile(path.join(buildDir, "formula_error_scan.txt"), errors.ndjson ?? String(errors), "utf8");

for (const sheetName of ["README", "PowerBI Preview", "DimRiskTier", "DimModule", "RiskSummary", "ModelMetrics", "ModelComparison", "FairnessAudit", "SHAPFactors", "Calibration", "DAX Measures", "Dashboard Spec"]) {
  const rendered = await wb.render({ sheetName, autoCrop: "all", scale: 0.8, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await rendered.arrayBuffer()));
}

const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(path.join(outputDir, "Student_Success_PowerBI_Data_Model.xlsx"));
console.log(`Saved workbook to ${path.join(outputDir, "Student_Success_PowerBI_Data_Model.xlsx")}`);
