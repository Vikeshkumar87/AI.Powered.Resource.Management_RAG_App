"""
frontend/app.py
Main Streamlit entry point with sidebar navigation.
Run: streamlit run frontend/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="AI Resource Management",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🤖 AI Resource Manager")
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Navigation**
- 📊 Dashboard — Workforce analytics
- 💬 AI Assistant — Natural language staffing
"""
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "_Powered by RAG · FastAPI · PostgreSQL · Streamlit_"
)

st.title("Welcome to the AI Resource Management Platform")
st.markdown(
    """
Use the sidebar to navigate between:

| Page | Purpose |
|---|---|
| 📊 **Dashboard** | View real-time workforce metrics, bench analytics, skill demand trends, and upcoming projects |
| 💬 **AI Assistant** | Submit natural language staffing requests and receive AI-ranked employee recommendations |
"""
)

st.info("Select a page from the sidebar to get started.", icon="👈")
