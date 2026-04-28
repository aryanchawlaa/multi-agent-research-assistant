import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests
import streamlit as st
from datetime import datetime

API_URL = "http://localhost:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 700;
        background: linear-gradient(135deg, #534AB7, #1D9E75);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header { color: #888; font-size: 1rem; margin-top: 0; }
    .agent-badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 0.8rem; font-weight: 600; margin-right: 6px;
    }
    .badge-searcher { background: #E1F5EE; color: #085041; }
    .badge-critic   { background: #FAECE7; color: #712B13; }
    .badge-writer   { background: #EEEDFE; color: #3C3489; }
    .metric-card {
        background: #f8f8f8; border-radius: 10px;
        padding: 14px 18px; border: 1px solid #eee;
    }
    .contradiction-box {
        background: #FFF3E0; border-left: 4px solid #FF9800;
        padding: 10px 14px; border-radius: 4px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    export_pdf = st.toggle("Export PDF", value=True, help="Generate a downloadable PDF")
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown("""
    <span class='agent-badge badge-searcher'>1 Searcher</span> arXiv + Web<br><br>
    <span class='agent-badge badge-critic'>2 Critic</span> Contradictions + Scores<br><br>
    <span class='agent-badge badge-writer'>3 Writer</span> Literature Review
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📌 Example Topics")
    examples = [
        "RAG for code generation",
        "Vision transformers in medical imaging",
        "Reinforcement learning from human feedback",
        "Graph neural networks for drug discovery",
        "Federated learning privacy guarantees",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["topic_input"] = ex

    st.markdown("---")
    st.caption("Powered by CrewAI · Qdrant · FastAPI")


# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-header'>Multi-Agent Research Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>3 specialized AI agents: Search → Critique → Write</p>", unsafe_allow_html=True)
st.markdown("---")

# Topic input
topic = st.text_input(
    "Research topic",
    value=st.session_state.get("topic_input", ""),
    placeholder="e.g. Large language models for code generation",
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("🚀 Run Research", type="primary", use_container_width=True)
with col2:
    st.caption("Estimated time: 3–6 minutes depending on topic complexity")

st.markdown("")

# ── Run research ───────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.error("Please enter a research topic.")
        st.stop()

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        health.raise_for_status()
    except Exception:
        st.error(
            "❌ Cannot connect to the API server. "
            "Make sure you ran: `uvicorn api.main:app --reload --port 8000`"
        )
        st.stop()

    # Submit job
    try:
        resp = requests.post(
            f"{API_URL}/research",
            json={"topic": topic, "export_pdf": export_pdf},
            timeout=10,
        )
        resp.raise_for_status()
        job = resp.json()
        job_id = job["job_id"]
    except Exception as e:
        st.error(f"Failed to start research job: {e}")
        st.stop()

    st.success(f"Job started! ID: `{job_id[:16]}...`")

    # Agent progress display
    st.markdown("### 🔄 Agent Pipeline Running")
    agent_cols = st.columns(3)
    agent_states = {
        "Searcher": ("🔍", "Searching arXiv & web...", "badge-searcher"),
        "Critic": ("🧐", "Waiting...", "badge-critic"),
        "Writer": ("✍️", "Waiting...", "badge-writer"),
    }

    with agent_cols[0]:
        searcher_ph = st.empty()
    with agent_cols[1]:
        critic_ph = st.empty()
    with agent_cols[2]:
        writer_ph = st.empty()

    progress_bar = st.progress(0, text="Initializing agents...")
    status_text = st.empty()

    start_time = time.time()
    max_wait = 600  # 10 min timeout
    poll_interval = 4

    elapsed_steps = 0
    while time.time() - start_time < max_wait:
        try:
            status_resp = requests.get(f"{API_URL}/research/{job_id}", timeout=10)
            job_data = status_resp.json()
        except Exception:
            time.sleep(poll_interval)
            continue

        elapsed = int(time.time() - start_time)
        elapsed_steps += 1
        pct = min(int(elapsed_steps * 1.5), 95)

        # Simulate agent stage updates
        if elapsed < 90:
            stage_msg = "🔍 Searcher: Querying arXiv and web sources..."
            searcher_ph.info("🔍 **Searcher** — Searching...")
            critic_ph.warning("🧐 **Critic** — Waiting...")
            writer_ph.warning("✍️ **Writer** — Waiting...")
        elif elapsed < 200:
            stage_msg = "🧐 Critic: Analyzing contradictions and credibility..."
            searcher_ph.success("🔍 **Searcher** — Done ✓")
            critic_ph.info("🧐 **Critic** — Analyzing...")
            writer_ph.warning("✍️ **Writer** — Waiting...")
        else:
            stage_msg = "✍️ Writer: Drafting the literature review..."
            searcher_ph.success("🔍 **Searcher** — Done ✓")
            critic_ph.success("🧐 **Critic** — Done ✓")
            writer_ph.info("✍️ **Writer** — Writing...")

        progress_bar.progress(pct, text=f"{stage_msg} ({elapsed}s elapsed)")

        if job_data["status"] == "done":
            progress_bar.progress(100, text="✅ Research complete!")
            searcher_ph.success("🔍 **Searcher** — Done ✓")
            critic_ph.success("🧐 **Critic** — Done ✓")
            writer_ph.success("✍️ **Writer** — Done ✓")
            status_text.success(f"Completed in {elapsed} seconds")

            # ── Results ────────────────────────────────────────────────────────
            result = job_data["result"]
            review = result.get("literature_review", "")
            word_count = result.get("word_count", len(review.split()))

            st.markdown("---")
            st.markdown("### 📊 Results Overview")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Word Count", f"{word_count:,}")
            m2.metric("Agents Used", "3")
            m3.metric("Time Taken", f"{elapsed}s")
            m4.metric("Topic", topic[:20] + "..." if len(topic) > 20 else topic)

            st.markdown("---")
            st.markdown("### 📄 Literature Review")

            # Highlight contradictions section
            if "Contradiction" in review or "contradiction" in review:
                st.info("⚠️ This review contains contradiction analysis — check Section 3.")

            st.markdown(review)

            # Download buttons
            st.markdown("---")
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label="⬇️ Download as Markdown",
                    data=review,
                    file_name=f"literature_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with dl_col2:
                if job_data.get("pdf_path") and os.path.exists(job_data["pdf_path"]):
                    with open(job_data["pdf_path"], "rb") as f:
                        st.download_button(
                            label="⬇️ Download as PDF",
                            data=f,
                            file_name=f"literature_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                else:
                    st.button("📄 PDF not generated", disabled=True, use_container_width=True)
            break

        elif job_data["status"] == "error":
            progress_bar.empty()
            st.error(f"❌ Research failed: {job_data.get('error', 'Unknown error')}")
            st.info("Check your API keys in the .env file and make sure Qdrant is running.")
            break

        time.sleep(poll_interval)

    else:
        st.warning("⏱️ Timed out after 10 minutes. The topic may be too broad — try being more specific.")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Multi-Agent Research Assistant · Built with CrewAI, LangChain, Qdrant, FastAPI, Streamlit")
