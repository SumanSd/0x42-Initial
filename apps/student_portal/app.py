"""Run: python -m streamlit run apps/student_portal/app.py --server.port 8502."""

import streamlit as st

st.set_page_config(page_title="Student | Skill Erosion Tracker")
st.title("Your next practice step")
st.info("Project skeleton: personalized exercises will appear after backend integration.")
st.subheader("Planned view")
st.markdown("""
- See a specific concept to practice and why it matters.
- Open an exercise and the curated resource that supports it.
- Submit an unassisted follow-up attempt to track progress.
""")
st.caption("The student view will show only the signed-in student's own learning information.")
