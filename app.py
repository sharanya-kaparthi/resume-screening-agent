import streamlit as st
import tempfile, os, json
from src.parser import parse_resume, parse_job_description
from src.scorer import score_resumes
from src.ranker import rank_candidates

st.set_page_config(page_title="HireIQ · Resume Screener", page_icon="🧠", layout="wide")

# ── Header ────────────────────────────────────────────────────
st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem 0'>
        <h1>🧠 HireIQ</h1>
        <p style='color: #94a3b8; font-size: 1.1rem'>
            AI-powered resume screening · Powered by HuggingFace
        </p>
    </div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=40)
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Shortlist top N candidates", 1, 20, 5)
    st.divider()
    st.markdown("**Model:** `all-MiniLM-L6-v2`")
    st.markdown("**Method:** Semantic similarity")
    st.markdown("**Deployment:** Streamlit Cloud (Free)")
    st.divider()
    st.markdown("Built for [Product Space Hackathon](https://productspace.in) 🚀")

# ── Step indicators ───────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.info("① Paste Job Description")
col2.info("② Upload Resumes")
col3.info("③ Click Screen")
col4.info("④ Get Ranked Results")

st.divider()

# ── JD Input ─────────────────────────────────────────────────
st.subheader("📋 Job Description")
jd_tab1, jd_tab2 = st.tabs(["✏️ Paste Text", "📁 Upload File"])
jd_dict = None

with jd_tab1:
    job_title = st.text_input("Job Title", placeholder="e.g. Backend Python Developer")
    jd_input = st.text_area("Full Job Description", height=180,
        placeholder="Paste the complete job description here...")
    if jd_input.strip():
        jd_dict = {"title": job_title or "Role", "raw_text": jd_input.strip()}

with jd_tab2:
    jd_file = st.file_uploader("Upload JD (.txt or .json)", type=["txt", "json"])
    if jd_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[-1]) as tmp:
            tmp.write(jd_file.read())
        jd_dict = parse_job_description(tmp.name)
        st.success(f"✅ Loaded: {jd_file.name}")

# ── Resume Upload ─────────────────────────────────────────────
st.subheader("📂 Candidate Resumes")
uploaded_resumes = st.file_uploader(
    "Upload resumes — PDF, DOCX, or TXT (multiple allowed)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)
if uploaded_resumes:
    st.caption(f"📎 {len(uploaded_resumes)} file(s) uploaded")

# ── Run ───────────────────────────────────────────────────────
st.divider()
run_btn = st.button("🚀 Screen Resumes Now", type="primary", use_container_width=True)

if run_btn:
    if not jd_dict:
        st.error("❌ Please provide a job description.")
        st.stop()
    if not uploaded_resumes:
        st.error("❌ Please upload at least one resume.")
        st.stop()

    resumes = []
    with st.status("📂 Parsing resumes...", expanded=True) as status:
        for f in uploaded_resumes:
            ext = os.path.splitext(f.name)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(f.read())
            try:
                parsed = parse_resume(tmp.name)
                parsed["id"] = os.path.splitext(f.name)[0]
                parsed["filename"] = f.name
                resumes.append(parsed)
                st.write(f"✅ {f.name}")
            except Exception as e:
                st.write(f"❌ {f.name} — {e}")
        status.update(label=f"✅ Parsed {len(resumes)} resumes", state="complete")

    if not resumes:
        st.error("No resumes could be parsed.")
        st.stop()

    with st.status("🧠 Running AI scoring via HuggingFace...", expanded=True) as status:
        try:
            scored = score_resumes(resumes, jd_dict)
            status.update(label="✅ Scoring complete!", state="complete")
        except Exception as e:
            st.error(f"HuggingFace API error: {e}")
            st.stop()

    ranked = rank_candidates(scored, top_n=top_n)
    shortlisted = [c for c in ranked if c["shortlisted"]]
    not_shortlisted = [c for c in ranked if not c["shortlisted"]]

    # ── Metrics ───────────────────────────────────────────────
    st.header("🏆 Screening Results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📄 Total Screened", len(ranked))
    m2.metric("✅ Shortlisted", len(shortlisted))
    m3.metric("❌ Rejected", len(not_shortlisted))
    m4.metric("🥇 Top Score", f"{ranked[0]['semantic_score']:.0%}" if ranked else "—")

    # ── Shortlisted ───────────────────────────────────────────
    st.subheader(f"✅ Shortlisted — Top {top_n} Candidates")
    for c in shortlisted:
        score_pct = int(c["semantic_score"] * 100)
        bar_color = "🟢" if score_pct >= 70 else "🟡" if score_pct >= 50 else "🔴"
        with st.expander(f"{bar_color} #{c['rank']} {c['id']} — {score_pct}% match"):
            st.progress(score_pct / 100)
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**File:** `{c['filename']}`")
            col_b.markdown(f"**Semantic Score:** `{c['semantic_score']}`")
            st.markdown("**Resume Preview:**")
            st.text(c.get("raw_text", "")[:600] + "...")

    # ── Not shortlisted ───────────────────────────────────────
    if not_shortlisted:
        with st.expander(f"❌ Not Shortlisted ({len(not_shortlisted)})"):
            for c in not_shortlisted:
                st.markdown(f"**#{c['rank']} {c['id']}** — `{c['semantic_score']:.0%}` match")

    # ── Download ──────────────────────────────────────────────
    st.divider()
    report = {
        "job_title": jd_dict.get("title"),
        "total_screened": len(ranked),
        "shortlisted": len(shortlisted),
        "ranked_candidates": [
            {"rank": c["rank"], "name": c["id"],
             "score": c["semantic_score"], "shortlisted": c["shortlisted"]}
            for c in ranked
        ]
    }
    st.download_button("📥 Download Report (JSON)", data=json.dumps(report, indent=2),
        file_name="hireiq_report.json", mime="application/json", use_container_width=True)
