"""
frontend/pages/1_Dashboard.py
Analytics Dashboard — KPI cards, bench table, skill charts, upcoming projects.
"""
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Resource Analytics Dashboard")
st.markdown("Real-time visibility into workforce utilization, bench status, and skill demand.")
st.markdown("---")


@st.cache_data(ttl=30)
def fetch_metrics():
    try:
        r = httpx.get(f"{BACKEND}/api/dashboard/metrics", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return None


@st.cache_data(ttl=30)
def fetch_bench_by_skill():
    try:
        r = httpx.get(f"{BACKEND}/api/dashboard/bench-by-skill", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


@st.cache_data(ttl=30)
def fetch_skill_demand():
    try:
        r = httpx.get(f"{BACKEND}/api/dashboard/skill-demand", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Fetch data ──────────────────────────────────────────────────
metrics = fetch_metrics()
bench_skills = fetch_bench_by_skill()
skill_demand = fetch_skill_demand()

if metrics is None:
    st.warning("Backend is not reachable. Start FastAPI with: `uvicorn backend.main:app --reload`")
    st.stop()

# ── KPI Cards ───────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Employees", metrics["total_employees"])
col2.metric("✅ Available (Bench)", metrics["available_resources"])
col3.metric("📉 Bench %", f"{metrics['bench_percentage']}%")
col4.metric("⚡ Avg Utilization", f"{metrics['avg_utilization']}%")

st.markdown("---")

# ── Charts Row ──────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🎯 Skill Demand (Active Projects)")
    if skill_demand:
        df_demand = pd.DataFrame(skill_demand)
        fig = px.bar(
            df_demand, x="count", y="skill", orientation="h",
            color="count", color_continuous_scale="Blues",
            labels={"count": "Projects requiring", "skill": "Skill"},
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No skill demand data available.")

with chart_col2:
    st.subheader("🪑 Bench by Skill")
    if bench_skills:
        df_bench = pd.DataFrame(bench_skills)
        fig2 = px.bar(
            df_bench, x="count", y="skill", orientation="h",
            color="count", color_continuous_scale="Oranges",
            labels={"count": "Employees on bench", "skill": "Skill"},
        )
        fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No bench skill data available.")

st.markdown("---")

# ── Utilization Gauge ───────────────────────────────────────────
gauge_col, proj_col = st.columns([1, 2])

with gauge_col:
    st.subheader("⚡ Utilization Gauge")
    util = metrics["avg_utilization"]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=util,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, 50], "color": "#ffcccc"},
                {"range": [50, 75], "color": "#fff3cc"},
                {"range": [75, 100], "color": "#ccffcc"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "value": 85},
        },
        title={"text": "Avg Utilization"},
    ))
    fig_gauge.update_layout(height=280)
    st.plotly_chart(fig_gauge, use_container_width=True)

with proj_col:
    st.subheader("🚀 Upcoming Projects")
    upcoming = metrics.get("upcoming_projects", [])
    if upcoming:
        df_proj = pd.DataFrame(upcoming)
        df_proj.columns = ["Project Name", "Resources Needed", "Start Date", "Domain"]
        st.dataframe(df_proj, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming project data.")

st.markdown("---")

# ── Bench Employee Table ─────────────────────────────────────────
st.subheader("🪑 Employees Currently on Bench")
bench_emps = metrics.get("bench_employees", [])
if bench_emps:
    df_emp = pd.DataFrame(bench_emps)
    df_emp["skills"] = df_emp["skills"].apply(lambda x: ", ".join(x) if x else "")
    df_emp.columns = ["ID", "Name", "Skills", "Experience (yrs)", "Bench Since", "Domain"]
    st.dataframe(df_emp, use_container_width=True, hide_index=True)
else:
    st.success("No employees on bench currently!")
