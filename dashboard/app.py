"""Minimal Streamlit dashboard for the Student Success Analytics prototype.
Apple-inspired design: clean, minimal, with generous whitespace and subtle depth.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "oulad"

# Apple Design System colors
BG = "#FFFFFF"
BG_SECONDARY = "#F5F5F7"
TEXT_PRIMARY = "#1D1D1F"
TEXT_SECONDARY = "#86868B"
ACCENT = "#007AFF"
ACCENT_LIGHT = "#E5F1FF"
GREEN = "#34C759"
ORANGE = "#FF9500"
RED = "#FF3B30"
BORDER = "#D2D2D7"
CARD_SHADOW = "rgba(0,0,0,0.04)"

# Risk tier colors (Apple-style subtle)
TIER_FG = {"High": RED, "Medium": ORANGE, "Low": GREEN}
TIER_BG = {"High": "#FFF5F5", "Medium": "#FFF9F0", "Low": "#F0FFF4"}
TIER_LABEL = {"High": "Review now", "Medium": "Watch", "Low": "On track"}

st.set_page_config(
    page_title="Student Success",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _css() -> str:
    return f"""
<style>
/* Apple Design System */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {{ box-sizing: border-box; }}
html, body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; -webkit-font-smoothing: antialiased; }}
.stApp {{ background: {BG}; color: {TEXT_PRIMARY}; }}
.block-container {{ max-width: 1100px; padding: 3rem 2.5rem 6rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {BG_SECONDARY};
    border-right: none;
}}
[data-testid="stSidebar"] > div:first-child {{ padding: 2rem 1.5rem; }}

/* Typography */
.page-eyebrow {{ color: {TEXT_SECONDARY}; font-size: .75rem; font-weight: 500; letter-spacing: .02em; text-transform: uppercase; margin-bottom: .4rem; }}
.page-title {{ color: {TEXT_PRIMARY}; font-size: 2.25rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; margin: 0 0 .5rem; }}
.page-sub {{ color: {TEXT_SECONDARY}; font-size: 1rem; line-height: 1.6; max-width: 600px; }}

/* Metric Cards */
.metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 2rem 0; }}
.metric-card {{
    background: {BG};
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}}
.metric-value {{ color: {TEXT_PRIMARY}; font-size: 2rem; font-weight: 600; letter-spacing: -.02em; line-height: 1; }}
.metric-label {{ color: {TEXT_SECONDARY}; font-size: .875rem; font-weight: 500; margin-top: .5rem; }}
.metric-note {{ color: {TEXT_SECONDARY}; font-size: .75rem; margin-top: .35rem; }}

/* Section Headers */
.section-header {{ margin: 2.5rem 0 1.25rem; }}
.section-title {{ color: {TEXT_PRIMARY}; font-size: 1.375rem; font-weight: 600; letter-spacing: -.01em; }}
.section-subtitle {{ color: {TEXT_SECONDARY}; font-size: .875rem; margin-top: .25rem; }}

/* Cards */
.info-card {{
    background: {BG};
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}}
.info-card h4 {{ color: {TEXT_PRIMARY}; font-size: 1rem; font-weight: 600; margin: 0 0 .5rem; }}
.info-card p {{ color: {TEXT_SECONDARY}; font-size: .9375rem; line-height: 1.6; margin: 0; }}

/* Student Strip */
.student-strip {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: {BG};
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}}
.student-name {{ font-size: 1.25rem; font-weight: 600; color: {TEXT_PRIMARY}; }}
.student-meta {{ font-size: .875rem; color: {TEXT_SECONDARY}; margin-top: .2rem; }}

/* Tiers */
.tier {{
    display: inline-flex;
    padding: .4rem .9rem;
    border-radius: 20px;
    font-size: .8125rem;
    font-weight: 600;
}}

/* Notice Banner */
.notice-banner {{
    background: {ACCENT_LIGHT};
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 1.5rem 0;
    font-size: .9375rem;
    color: #004B8E;
    line-height: 1.5;
}}
.notice-banner strong {{ font-weight: 600; }}
.notice-banner.warning {{ background: #FFF5E6; color: #8B5A00; }}

/* Form Controls */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border-color: {BORDER} !important;
    background: {BG} !important;
}}
.stTextInput > div > div,
.stSelectbox > div > div {{
    border-radius: 10px;
    border: 1px solid {BORDER};
}}
[data-testid="stTextInput"] input {{
    border-radius: 10px;
    border: 1px solid {BORDER};
    padding: .6rem 1rem;
}}
[data-testid="stMultiSelect"] {{
    border-radius: 10px;
}}
[data-baseweb="radio"] {{ gap: .5rem; }}
[data-baseweb="radio"] label {{
    background: {BG};
    border-radius: 10px;
    padding: .75rem 1rem;
    border: 1px solid {BORDER};
    font-weight: 500;
}}
[data-baseweb="radio"] label:hover {{ border-color: {ACCENT}; }}
[data-baseweb="radio"] input:checked + div {{
    background: {ACCENT} !important;
    color: white !important;
    border-color: {ACCENT} !important;
}}

/* DataFrame */
[data-testid="stDataFrame"] {{
    border: none;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
[data-testid="stTable"] {{ border-radius: 12px; }}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    border-bottom: 1px solid {BORDER};
    gap: .5rem;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    color: {TEXT_SECONDARY};
    font-size: .9375rem;
    font-weight: 500;
    padding: .75rem 1rem;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    color: {ACCENT};
    border-bottom-color: {ACCENT};
}}

/* Expander */
[data-testid="stExpander"] {{
    background: {BG};
    border-radius: 12px;
    border: 1px solid {BORDER};
}}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {{ color: {TEXT_SECONDARY}; }}

/* Hide Streamlit elements */
#MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* Sidebar branding */
.brand-mark {{
    width: 40px;
    height: 40px;
    background: {ACCENT};
    border-radius: 10px;
    display: grid;
    place-items: center;
    color: white;
    font-weight: 700;
    font-size: .875rem;
    margin-bottom: 1rem;
}}
.brand-title {{ font-size: 1.125rem; font-weight: 600; color: {TEXT_PRIMARY}; }}
.brand-sub {{ font-size: .8125rem; color: {TEXT_SECONDARY}; margin-top: .25rem; }}

/* Sidebar nav */
.sidebar-nav {{
    display: flex;
    flex-direction: column;
    gap: .35rem;
    margin-top: 1.5rem;
}}
.nav-item {{
    display: block;
    padding: .75rem 1rem;
    border-radius: 10px;
    color: {TEXT_PRIMARY};
    text-decoration: none;
    font-weight: 500;
    font-size: .9375rem;
    transition: background .15s;
}}
.nav-item:hover {{ background: rgba(0,0,0,0.04); }}
.nav-item.active {{
    background: {ACCENT};
    color: white;
}}
.sidebar-note {{
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid {BORDER};
    color: {TEXT_SECONDARY};
    font-size: .75rem;
    line-height: 1.6;
}}

/* Progress column */
[data-testid="stDataFrame"] .stDataFramePrimary {{
    border-radius: 8px;
}}

/* Chips/Tags white text fix */
[data-baseweb="tag"] *, [data-testid="stTag"] * {{ color: white !important; }}

/* Responsive */
@media (max-width: 900px) {{
    .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .block-container {{ padding: 2rem 1.5rem 4rem; }}
}}
</style>
"""


st.markdown(_css(), unsafe_allow_html=True)


def pct(value: float) -> str:
    return f"{value:.1%}"


def safe_pct(value: object) -> str:
    return pct(float(value)) if pd.notna(value) else "Not available"


def page_header(title: str, subtitle: str, badge: str = "") -> None:
    badge_html = f'<span style="background:{BG_SECONDARY};padding:.4rem .9rem;border-radius:20px;font-size:.75rem;font-weight:500;color:{TEXT_SECONDARY};">{badge}</span>' if badge else ""
    st.markdown(
        f'<div style="margin-bottom:1rem;"><div class="page-eyebrow">Student Success</div>'
        f'<div class="page-title">{title}</div><div class="page-sub">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def metric_grid(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div><div class="metric-note">{note}</div></div>'
        for label, value, note in items
    )
    st.markdown(f'<div class="metric-grid">{cards}</div>', unsafe_allow_html=True)


def section_header(title: str, help_text: str = "") -> None:
    subtitle_html = f'<div class="section-subtitle">{help_text}</div>' if help_text else ""
    st.markdown(f'<div class="section-header"><div class="section-title">{title}</div>{subtitle_html}</div>', unsafe_allow_html=True)


def tier_html(tier: str) -> str:
    return f'<span class="tier" style="color:{TIER_FG[tier]};background:{TIER_BG[tier]};">{TIER_LABEL[tier]}</span>'


def clean_text(value: object, fallback: str) -> str:
    return fallback if pd.isna(value) or not str(value).strip() else str(value)


@st.cache_data
def load_artifacts():
    queue = pd.read_csv(ARTIFACTS / "faculty_review_queue.csv")
    comparison = pd.read_csv(ARTIFACTS / "model_comparison.csv")
    fairness = pd.read_csv(ARTIFACTS / "fairness_audit.csv")
    risk_summary = pd.read_csv(ARTIFACTS / "risk_tier_summary.csv")
    shap_global = pd.read_csv(ARTIFACTS / "explanations" / "shap_global.csv")
    shap_local = pd.read_csv(ARTIFACTS / "explanations" / "shap_local_sample.csv")
    evaluation = json.loads((ARTIFACTS / "evaluation.json").read_text(encoding="utf-8"))
    calibration = pd.read_csv(ARTIFACTS / "calibration_curve.csv")
    return queue, comparison, fairness, risk_summary, shap_global, shap_local, evaluation, calibration


def faculty_view(queue: pd.DataFrame, shap_global: pd.DataFrame, shap_local: pd.DataFrame) -> None:
    page_header("Faculty Dashboard", "Find students who may need support and take timely action.")
    st.markdown('<div class="notice-banner"><strong>Decision support only</strong> — Review the full context before contacting students. Never use this score to change grades or academic status.</div>', unsafe_allow_html=True)

    total = len(queue)
    high_count = int(queue["risk_tier"].eq("High").sum())
    medium_count = int(queue["risk_tier"].eq("Medium").sum())
    low_count = int(queue["risk_tier"].eq("Low").sum())
    metric_grid([
        ("Review now", f"{high_count:,}", f"{high_count / total:.0%} of students"),
        ("Watch", f"{medium_count:,}", f"{medium_count / total:.0%}"),
        ("On track", f"{low_count:,}", f"{low_count / total:.0%}"),
        ("Total", f"{total:,}", "Across all modules"),
    ])

    section_header("Find Students")
    with st.container():
        c1, c2, c3 = st.columns([1.5, 1, 1], gap="small")
        modules = sorted(queue["code_module"].unique())
        with c1:
            sel_modules = st.multiselect("Module", modules, default=modules, label_visibility="collapsed")
        with c2:
            sel_tiers = st.multiselect("Priority", ["High", "Medium", "Low"], default=["High"], label_visibility="collapsed")
        with c3:
            sort_opt = st.selectbox("Sort by", ["Highest probability", "Longest inactive", "Student ID"], label_visibility="collapsed")

    search = st.text_input("Search by student ID", placeholder="Enter student ID...", label_visibility="collapsed")

    filtered = queue[queue["code_module"].isin(sel_modules) & queue["risk_tier"].isin(sel_tiers)].copy()
    sort_col, ascending = {
        "Highest probability": ("adverse_probability", False),
        "Longest inactive": ("days_since_last_activity", False),
        "Student ID": ("id_student", True),
    }[sort_opt]
    filtered = filtered.sort_values(sort_col, ascending=ascending)
    if search.strip():
        filtered = filtered[filtered["id_student"].astype(str).str.contains(search.strip(), regex=False)]

    section_header("Students to Review", f"{len(filtered):,} matching")
    if filtered.empty:
        st.info("No students match these filters.")
        return

    table = filtered[["id_student", "code_module", "risk_tier", "adverse_probability", "days_since_last_activity", "support_indicators"]].copy()
    table["risk_tier"] = table["risk_tier"].map(TIER_LABEL)
    table.columns = ["Student", "Module", "Priority", "Model estimate", "Days inactive", "What to check"]
    st.dataframe(
        table, width="stretch", hide_index=True, height=280,
        column_config={
            "Student": st.column_config.NumberColumn("Student", format="%d"),
            "Model estimate": st.column_config.ProgressColumn("Model estimate", min_value=0.0, max_value=1.0, format="%.0f%%"),
            "Days inactive": st.column_config.NumberColumn("Days inactive", format="%d days"),
        },
    )

    section_header("Review Student")
    choices = filtered.apply(lambda row: f"{int(row.id_student)} | {row.code_module} | {TIER_LABEL[row.risk_tier]}", axis=1).tolist()
    selection = st.selectbox("Student record", choices)
    sid, module, _ = [part.strip() for part in selection.split("|")]
    row = filtered[filtered["id_student"].eq(int(sid)) & filtered["code_module"].eq(module)].iloc[0]

    st.markdown(
        f'<div class="student-strip"><div><div class="student-name">Student {int(row.id_student)}</div>'
        f'<div class="student-meta">Module {row.code_module} · Historical Day-40 record</div></div>{tier_html(row.risk_tier)}</div>',
        unsafe_allow_html=True,
    )
    metric_grid([
        ("Model estimate", pct(row.adverse_probability), "Historical estimate"),
        ("Assessment completion", safe_pct(row.get("assessment_completion_rate")), "Submitted when due"),
        ("Days inactive", f"{int(row.days_since_last_activity)}", "Since last activity"),
        ("Recent clicks", f"{int(row.get('clicks_last_14d', 0))}", "Last 14 days"),
    ])

    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown(f'<div class="info-card"><h4>What to check</h4><p>{clean_text(row.support_indicators, "No specific indicator available.")}</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown(f'<div class="info-card"><h4>Possible support</h4><p>{clean_text(row.faculty_review_options, "Discuss with the student and identify suitable support.")}</p></div>', unsafe_allow_html=True)

    with st.expander("Why did the model produce this estimate?"):
        st.caption("SHAP shows feature influence. It does not explain the cause of difficulty.")
        local = shap_local[shap_local["id_student"].eq(int(sid)) & shap_local["code_module"].eq(module)].sort_values("rank")
        if not local.empty:
            explanation = local[["feature", "feature_value", "shap_value_for_adverse_outcome"]].copy()
            explanation.columns = ["Feature", "Recorded value", "Effect on estimate"]
            st.dataframe(explanation, width="stretch", hide_index=True)
        else:
            chart_data = shap_global.head(10).sort_values("mean_abs_shap")
            figure = px.bar(chart_data, x="mean_abs_shap", y="feature", orientation="h", labels={"mean_abs_shap": "Average influence", "feature": ""}, color_discrete_sequence=[ACCENT])
            figure.update_layout(height=300, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY))
            figure.update_xaxes(showgrid=True, gridcolor=BORDER)
            figure.update_yaxes(showgrid=False)
            st.plotly_chart(figure, width="stretch")


def student_view(queue: pd.DataFrame) -> None:
    page_header("Student Progress", "A simple view of your learning records and available support.")
    st.markdown('<div class="notice-banner"><strong>For information only</strong> — This does not diagnose ability. Online activity does not capture every form of study.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="small")
    with c1:
        student_id = st.selectbox("Student", sorted(queue["id_student"].unique()))
    records = queue[queue["id_student"].eq(student_id)]
    with c2:
        module = st.selectbox("Module", sorted(records["code_module"].unique()))

    record = records[records["code_module"].eq(module)].iloc[0]
    score = record.get("assessment_score_mean", float("nan"))
    metric_grid([
        ("Assessments", f"{int(record.assessments_submitted)} / {int(record.assessments_due)}", "Submitted / due"),
        ("Average score", f"{score:.1f}" if pd.notna(score) else "N/A", "Available assessments"),
        ("Active days", f"{int(record.active_days)}", "VLE activity days"),
        ("Recent clicks", f"{int(record.clicks_last_14d)}", "Last 14 days"),
    ])

    activity_col, support_col = st.columns([1.2, 1], gap="medium")
    with activity_col:
        section_header("Recent Activity")
        activity = pd.DataFrame({"Week": ["Previous 7 days", "Most recent 7 days"], "Clicks": [record.clicks_previous_7d, record.clicks_last_7d]})
        figure = px.bar(activity, x="Week", y="Clicks", text="Clicks", color="Week", color_discrete_sequence=["#D1D5DB", ACCENT])
        figure.update_traces(textposition="outside", marker_line_width=0)
        figure.update_layout(height=260, showlegend=False, margin=dict(l=8, r=8, t=16, b=24), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY), yaxis=dict(showgrid=True, gridcolor=BORDER, title=""), xaxis=dict(title=""))
        st.plotly_chart(figure, width="stretch")
    with support_col:
        section_header("Support Available")
        st.markdown(f'<div class="info-card" style="min-height:260px;"><h4>Suggested next step</h4><p>{clean_text(record.faculty_review_options, "Contact your tutor to discuss your progress.")}</p><p style="margin-top:1rem;color:{TEXT_SECONDARY};font-size:.875rem;">Your tutor has context not shown here.</p></div>', unsafe_allow_html=True)


def evaluation_view(comparison, fairness, risk_summary, shap_global, evaluation, calibration) -> None:
    metrics = evaluation["test_metrics"]
    page_header("Model & Fairness", "Performance metrics and fairness checks for the prediction model.", "Test set: 2014J")
    st.markdown('<div class="notice-banner warning"><strong>Historical evidence</strong> — Results describe a held-out OULAD cohort. Not guaranteed for future students.</div>', unsafe_allow_html=True)

    metric_grid([
        ("ROC-AUC", f"{metrics['roc_auc']:.3f}", "Ranking performance"),
        ("PR-AUC", f"{metrics['average_precision']:.3f}", "Adverse-outcome focus"),
        ("High recall", pct(metrics["high_risk_recall"]), "Cases found"),
        ("High precision", pct(metrics["high_risk_precision"]), "Confirmed alerts"),
    ])

    perf_tab, fair_tab, factor_tab = st.tabs(["Performance", "Fairness", "Factors"])
    with perf_tab:
        left, right = st.columns(2, gap="medium")
        with left:
            section_header("Models Compared")
            model_table = comparison.round(4).copy()
            model_table.columns = [column.replace("_", " ").title() for column in model_table.columns]
            st.dataframe(model_table, width="stretch", hide_index=True, height=min(260, 42 * len(model_table) + 38))
        with right:
            section_header("Risk Distribution")
            tier_chart = px.bar(risk_summary, x="risk_tier", y="rows", color="risk_tier", category_orders={"risk_tier": ["Low", "Medium", "High"]}, color_discrete_map={"Low": GREEN, "Medium": ORANGE, "High": RED}, labels={"rows": "Students", "risk_tier": ""})
            tier_chart.update_layout(height=260, showlegend=False, margin=dict(l=8, r=8, t=16, b=24), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY), yaxis=dict(showgrid=True, gridcolor=BORDER))
            st.plotly_chart(tier_chart, width="stretch")

        section_header("Calibration", "Predicted vs observed outcomes")
        if not calibration.empty:
            chart = go.Figure()
            chart.add_trace(go.Scatter(x=calibration["mean_predicted_probability"], y=calibration["observed_adverse_fraction"], mode="lines+markers", name="Model", line=dict(color=ACCENT, width=3)))
            chart.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfect", line=dict(color="#D1D5DB", width=2, dash="dot")))
            chart.update_layout(height=280, margin=dict(l=8, r=8, t=12, b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY), xaxis=dict(title="Predicted probability", range=[0, 1], gridcolor=BORDER), yaxis=dict(title="Observed rate", range=[0, 1], gridcolor=BORDER))
            st.plotly_chart(chart, width="stretch")

    with fair_tab:
        section_header("Subgroup Comparison", "Differences are signals to investigate, not proof of unfair treatment")
        attribute = st.selectbox("Choose attribute", sorted(fairness["attribute"].unique()))
        subgroup_table = fairness[fairness["attribute"].eq(attribute)].round(4).copy()
        subgroup_table.columns = [column.replace("_", " ").title() for column in subgroup_table.columns]
        st.dataframe(subgroup_table, width="stretch", hide_index=True)

    with factor_tab:
        section_header("Feature Influence", "Largest average SHAP values")
        chart_data = shap_global.head(15).sort_values("mean_abs_shap")
        feature_chart = px.bar(chart_data, x="mean_abs_shap", y="feature", orientation="h", labels={"mean_abs_shap": "Average influence", "feature": ""}, color_discrete_sequence=[ACCENT])
        feature_chart.update_layout(height=400, margin=dict(l=8, r=8, t=8, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY), xaxis=dict(showgrid=True, gridcolor=BORDER))
        feature_chart.update_yaxes(showgrid=False)
        st.plotly_chart(feature_chart, width="stretch")
        st.caption("SHAP describes model behavior, not personal cause.")


def main() -> None:
    queue, comparison, fairness, risk_summary, shap_global, shap_local, evaluation, calibration = load_artifacts()

    with st.sidebar:
        st.markdown('<div class="brand-mark">SSA</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-title">Student Success</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">Analytics</div>', unsafe_allow_html=True)

        view = st.radio("", ["Faculty dashboard", "Student progress", "Model & fairness"], label_visibility="collapsed")
        st.markdown('<div class="sidebar-note">OULAD research prototype<br>Day-40 snapshot<br>No automated decisions</div>', unsafe_allow_html=True)

    if view == "Faculty dashboard":
        faculty_view(queue, shap_global, shap_local)
    elif view == "Student progress":
        student_view(queue)
    else:
        evaluation_view(comparison, fairness, risk_summary, shap_global, evaluation, calibration)


if __name__ == "__main__":
    main()
