"""
frontend/pages/2_AI_Assistant.py
Conversational AI staffing assistant using the RAG backend.
"""
import streamlit as st
import httpx
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Assistant", page_icon="💬", layout="wide")
st.title("💬 AI Staffing Assistant")
st.markdown(
    "Ask in plain English. The AI will retrieve the best-matched employees from the database "
    "and explain why they fit your requirements."
)
st.markdown("---")

# ── Example prompts ─────────────────────────────────────────────
with st.expander("💡 Example queries you can ask", expanded=False):
    st.markdown("""
- *Find two available Python developers with Azure experience for a healthcare project.*
- *Suggest Java developers with AWS experience for a banking portal.*
- *Who are the best GenAI engineers available right now?*
- *Find a DevOps engineer with Kubernetes and Terraform skills.*
- *Recommend a senior project manager for an agile banking programme.*
""")

# ── Configuration sidebar ────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Query Settings")
    top_k = st.slider("Number of recommendations", min_value=1, max_value=5, value=3)
    st.markdown("---")
    st.caption("Backend: " + BACKEND)

# ── Chat state ───────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ── Chat input ───────────────────────────────────────────────────
query = st.chat_input("Describe your staffing requirement...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Call RAG backend
    with st.chat_message("assistant"):
        with st.spinner("Searching employee profiles and generating recommendations..."):
            try:
                response = httpx.post(
                    f"{BACKEND}/api/rag/query",
                    json={"query": query, "top_k": top_k},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
            except httpx.ConnectError:
                st.error("Cannot connect to backend. Ensure FastAPI is running on port 8000.")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        if "error" in data:
            st.warning(f"⚠️ {data['error']}")

        recommendations = data.get("recommendations", [])
        summary = data.get("summary", "")

        if not recommendations:
            reply = "No suitable candidates found for your request. Try broadening the criteria."
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            # Build formatted response
            reply_parts = []

            if summary:
                st.info(summary)
                reply_parts.append(f"**Summary:** {summary}")

            for i, rec in enumerate(recommendations, 1):
                score = rec.get("match_score", 0)
                name = rec.get("name", "Unknown")
                emp_id = rec.get("employee_id", "")
                reasons = rec.get("reasons", [])
                gaps = rec.get("skill_gaps", [])
                suggestions = rec.get("upskilling_suggestions", [])

                # Color-coded badge
                if score >= 85:
                    badge = "🟢"
                elif score >= 70:
                    badge = "🟡"
                else:
                    badge = "🔴"

                st.markdown(f"### {badge} {i}. {name} — **{score}% Match** `{emp_id}`")

                col_r, col_g = st.columns(2)
                with col_r:
                    st.markdown("**✅ Why they fit:**")
                    for r in reasons:
                        st.markdown(f"- {r}")
                with col_g:
                    if gaps:
                        st.markdown("**⚠️ Skill Gaps:**")
                        for g in gaps:
                            st.markdown(f"- {g}")
                    if suggestions:
                        st.markdown("**📚 Upskilling:**")
                        for s in suggestions:
                            st.markdown(f"- {s}")

                st.markdown("---")

                reply_parts.append(
                    f"{badge} **{name}** ({emp_id}) — {score}% match\n"
                    + "\n".join(f"  - {r}" for r in reasons)
                )

            full_reply = "\n\n".join(reply_parts)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})

# ── Clear chat ───────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
