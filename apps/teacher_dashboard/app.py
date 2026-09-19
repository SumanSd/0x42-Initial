"""Run: python -m streamlit run apps/teacher_dashboard/app.py --server.port 8501."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from skill_erosion.data import load_expected_trends, load_synthetic_attempts
from skill_erosion.orchestration.pipeline import run_journey

st.set_page_config(page_title="Teacher | Skill Erosion Tracker", layout="wide")
st.title("Teacher trend dashboard")
st.caption("Synthetic pilot data only. Scores are heuristics, not assessments of real students.")

expected = load_expected_trends()
students = sorted(expected)

if "seeded" not in st.session_state:
    st.session_state.seeded = False

col_seed, _ = st.columns([1, 3])
if col_seed.button("Load / refresh synthetic data", type="primary"):
    from skill_erosion.agents.trace_collector.agent import collect_traces

    result = collect_traces(load_synthetic_attempts())
    st.session_state.seeded = True
    st.success(f"Stored {len(result.attempt_ids)} attempts ({result.stored_versions} versions). Reimport is a no-op.")

student_id = st.selectbox("Student", students)
skill_id = expected[student_id]["skill_id"]

if not st.session_state.seeded:
    st.info("Load the synthetic data first.")

if st.session_state.seeded and st.button("Run analysis"):
    result = asyncio.run(run_journey(None, student_id, skill_id))
    trend = result.trend

    st.subheader(f"{student_id} - {skill_id}")
    status_col, model_col = st.columns(2)
    status_col.metric("Trend status", trend.status)
    model_col.metric("Model version", trend.model_version)
    st.write(trend.explanation)

    if trend.checkpoints:
        chart = {
            "assisted": [c.assisted_score for c in trend.checkpoints],
            "unassisted": [c.unassisted_score for c in trend.checkpoints],
            "gap": [c.gap for c in trend.checkpoints],
        }
        st.line_chart(chart, x=[c.checkpoint_id for c in trend.checkpoints])
        st.dataframe(
            [
                {
                    "checkpoint": c.checkpoint_id,
                    "assisted": c.assisted_score,
                    "unassisted": c.unassisted_score,
                    "gap": c.gap,
                    "evidence": ", ".join(c.evidence_attempt_ids),
                }
                for c in trend.checkpoints
            ],
            use_container_width=True,
        )

    st.subheader("Misconceptions and interventions")
    if not result.clusters:
        st.write("No recurring misconception clusters found in the stored evidence.")
    for cluster, plan in zip(result.clusters, result.remediation):
        with st.expander(f"{cluster.cluster_id}: {cluster.concept_summary}"):
            st.write(f"Evidence: {', '.join(cluster.evidence_attempt_ids)}")
            st.write(f"Plan status: {plan.status}")
            if plan.teacher_summary:
                st.write(plan.teacher_summary)
