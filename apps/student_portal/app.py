"""Run: python -m streamlit run apps/student_portal/app.py --server.port 8502."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from skill_erosion.data import (
    load_expected_trends,
    load_resource_body,
    load_resource_catalog,
    load_synthetic_attempts,
)
from skill_erosion.orchestration.pipeline import run_journey

st.set_page_config(page_title="Student | Skill Erosion Tracker")
st.title("Your next practice step")
st.caption("Demo view over synthetic data. You only see the selected learner's own plan.")

expected = load_expected_trends()
students = sorted(expected)

if "seeded" not in st.session_state:
    st.session_state.seeded = False

if st.button("Load / refresh synthetic data", type="primary"):
    from skill_erosion.agents.trace_collector.agent import collect_traces

    collect_traces(load_synthetic_attempts())
    st.session_state.seeded = True
    st.success("Synthetic data ready.")

student_id = st.selectbox("Learner", students)
skill_id = expected[student_id]["skill_id"]

if not st.session_state.seeded:
    st.info("Load the synthetic data first.")

if st.session_state.seeded and st.button("Get my practice step"):
    result = asyncio.run(run_journey(None, student_id, skill_id))
    ready = [p for p in result.remediation if p.status == "ready"]

    if not ready:
        st.write(
            "No targeted exercise yet. "
            "Keep completing the weekly unassisted checkpoints so a plan can be built."
        )
    else:
        plan = ready[0]
        cluster = next(c for c in result.clusters if c.cluster_id == plan.cluster_id)
        st.subheader(cluster.concept_summary)
        st.write(plan.student_exercise)
        catalog = {r["resource_id"]: r for r in load_resource_catalog()}
        for resource_id in plan.resource_ids:
            resource = catalog.get(resource_id)
            if resource:
                with st.expander(f"Resource: {resource_id}"):
                    st.markdown(load_resource_body(resource))
