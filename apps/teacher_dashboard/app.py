"""Run: python -m streamlit run apps/teacher_dashboard/app.py --server.port 8501."""

import streamlit as st

st.set_page_config(page_title="Teacher | Skill Erosion Tracker", layout="wide")
st.title("Teacher trend dashboard")
st.info("Project skeleton: the dashboard is not connected to student data yet.")
st.subheader("Planned view")
st.markdown("""
- Select a student and skill.
- Compare assisted and unassisted scores over at least three checkpoints.
- Show the gap trend, evidence sufficiency, and contradictory signals.
- Review a short misconception-specific intervention summary.
""")
st.caption("Use synthetic data during development. No student scores are computed here.")
