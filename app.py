import streamlit as st
import tempfile, os, json
from src.parser import parse_resume, parse_job_description
from src.scorer import score_resumes
from src.ranker import rank_candidates

st.set_page_config(page_title="HireIQ", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #000000 !important;
    color: #ffffff !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stAppViewContainer"] { background: #000 !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stApp { background: #000 !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Main container */
.main .block-container {
    max-width: 1100px;
    padding: 0 2rem 4rem 2rem !important;
    margin: 0 auto;
}

/* ── HERO ── */
.hireiq-hero {
    text-align: center;
    padding: 5rem 0 3.5rem 0;
    position: relative;
}
.hireiq-hero::after {
    content: '';
    display: block;
    width: 1px;
    height: 60px;
    background: linear-gradient(to bottom, #fff, transparent);
    margin: 2.5rem auto 0 auto;
}
.hireiq-wordmark {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 5rem;
    letter-spacing: 0.35em;
    color: #ffffff;
    text-transform: uppercase;
    line-height: 1;
}
.hireiq-tagline {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    color: #555;
    text-transform: uppercase;
    margin-top: 0.75rem;
}

/* ── DIVIDER ── */
.hiq-divider {
    border: none;
    border-top: 1px solid #1a1a1a;
    margin: 2rem 0;
}

/* ── SECTION LABEL ── */
.hiq-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: #444;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0a0a0a !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #fff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #fff !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput label, .stTextArea label {
    color: #444 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    border: 1px solid #1c1c1c !important;
    border-radius: 0 !important;
    background: #080808 !important;
    padding: 2rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #333 !important; }
[data-testid="stFileUploader"] label {
    color: #666 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 1px dashed #222 !important;
    border-radius: 0 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1a1a1a !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #444 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 0 !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #fff !important;
    border-bottom: 1px solid #fff !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0 0 !important; }

/* ── BUTTON ── */
.stButton > button {
    background: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.3em !important;
    text-transform: uppercase !important;
    padding: 1rem 2rem !important;
    width: 100% !important;
    transition: background 0.2s, color 0.2s;
    cursor: pointer;
}
.stButton > button:hover {
    background: #e0e0e0 !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #fff !important;
    border: 1px solid #333 !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    transition: border-color 0.2s;
}
.stDownloadButton > button:hover { border-color: #fff !important; }

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #080808 !important;
    border: 1px solid #1a1a1a !important;
    padding: 1.5rem !important;
    border-radius: 0 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    color: #444 !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #fff !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #080808 !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 0 !important;
    color: #fff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.2s;
}
.streamlit-expanderHeader:hover { border-color: #333 !important; }
.streamlit-expanderContent {
    background: #050505 !important;
    border: 1px solid #1a1a1a !important;
    border-top: none !important;
    padding: 1.25rem !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div {
    background: #ffffff !important;
    border-radius: 0 !important;
    height: 2px !important;
}
.stProgress > div > div {
    background: #111 !important;
    border-radius: 0 !important;
    height: 2px !important;
}

/* ── STATUS ── */
[data-testid="stStatusWidget"] {
    background: #080808 !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
}

/* ── ALERTS ── */
.stAlert {
    background: #0a0a0a !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #888 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
}

/* ── SCORE CARD ── */
.score-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    border: 1px solid #1a1a1a;
    background: #080808;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.score-card:hover { border-color: #333; }
.score-rank {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #333;
    width: 2rem;
}
.score-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #fff;
    flex: 1;
    padding: 0 1rem;
}
.score-pct {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #fff;
}
.score-bar-wrap {
    width: 120px;
    height: 1px;
    background: #1a1a1a;
    margin-left: 1.5rem;
    position: relative;
}
.score-bar-fill {
    position: absolute;
    top: 0; left: 0;
    height: 1px;
    background: #fff;
    transition: width 1s ease;
}
.badge-shortlisted {
    font-family: 'Space Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.15em;
    color: #000;
    background: #fff;
    padding: 0.2rem 0.6rem;
    margin-left: 1rem;
    text-transform: uppercase;
}
.badge-rejected {
    font-family: 'Space Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.15em;
    color: #333;
    border: 1px solid #1a1a1a;
    padding: 0.2rem 0.6rem;
    margin-left: 1rem;
    text-transform: uppercase;
}

/* ── SLIDER ── */
.stSlider > div > div > div { background: #fff !important; }
.stSlider label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    color: #444 !important;
    text-transform: uppercase !important;
}
</style>

<div class="hireiq-hero">
    <div class="hireiq-wordmark">HireIQ</div>
    <div class="hireiq-tagline">Intelligent Candidate Screening</div>
</div>
""", unsafe_allow_html=True)

# ── JOB DESCRIPTION ───────────────────────────────────────────
st.markdown('<div class="hiq-label">Job Description</div>', unsafe_allow_html=True)
jd_tab1, jd_tab2 = st.tabs(["Write", "Upload"])
jd_dict = None

with jd_tab1:
    job_title = st.text_input("", placeholder="Job title  e.g. Senior Backend Engineer", label_visibility="collapsed")
    jd_input = st.text_area("", height=160,
        placeholder="Paste the full job description here — requirements, responsibilities, and skills...",
        label_visibility="collapsed")
    if jd_input.strip():
        jd_dict = {"title": job_title.strip() or "Role", "raw_text": jd_input.strip()}

with jd_tab2:
    jd_file = st.file_uploader("", type=["txt", "json"], label_visibility="collapsed")
    if jd_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[-1]) as tmp:
            tmp.write(jd_file.read())
        try:
            jd_dict = parse_job_description(tmp.name)
            st.markdown(f'<div class="hiq-label">✓ Loaded — {jd_file.name}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

st.markdown('<hr class="hiq-divider">', unsafe_allow_html=True)

# ── RESUMES ───────────────────────────────────────────────────
st.markdown('<div class="hiq-label">Candidate Resumes</div>', unsafe_allow_html=True)
uploaded_resumes = st.file_uploader("",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)
if uploaded_resumes:
    st.markdown(f'<div class="hiq-label">✓ {len(uploaded_resumes)} file{"s" if len(uploaded_resumes) > 1 else ""} ready</div>',
        unsafe_allow_html=True)

st.markdown('<hr class="hiq-divider">', unsafe_allow_html=True)

# ── SETTINGS ─────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])
with col_right:
    top_n = st.slider("Shortlist size", 1, 20, 5)

with col_left:
    run_btn = st.button("Screen Candidates")

st.markdown('<hr class="hiq-divider">', unsafe_allow_html=True)

# ── RUN ───────────────────────────────────────────────────────
if run_btn:
    if not jd_dict:
        st.error("Provide a job description to continue.")
        st.stop()
    if not uploaded_resumes:
        st.error("Upload at least one resume to continue.")
        st.stop()

    resumes = []
    with st.status("Parsing resumes...", expanded=False) as status:
        for f in uploaded_resumes:
            ext = os.path.splitext(f.name)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(f.read())
            try:
                parsed = parse_resume(tmp.name)
                parsed["id"] = os.path.splitext(f.name)[0]
                parsed["filename"] = f.name
                resumes.append(parsed)
            except Exception as e:
                st.write(f"Could not parse {f.name}: {e}")
        status.update(label=f"{len(resumes)} resume{'s' if len(resumes)>1 else ''} parsed", state="complete")

    if not resumes:
        st.error("No resumes could be parsed. Check your file formats.")
        st.stop()

    with st.status("Analysing candidates...", expanded=False) as status:
        try:
            scored = score_resumes(resumes, jd_dict)
            status.update(label="Analysis complete", state="complete")
        except Exception as e:
            st.error(f"Scoring error: {e}")
            st.stop()

    ranked = rank_candidates(scored, top_n=top_n)
    shortlisted = [c for c in ranked if c["shortlisted"]]
    not_shortlisted = [c for c in ranked if not c["shortlisted"]]

    # ── METRICS ──────────────────────────────────────────────
    st.markdown('<div class="hiq-label">Overview</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Screened", len(ranked))
    m2.metric("Shortlisted", len(shortlisted))
    m3.metric("Not Selected", len(not_shortlisted))
    m4.metric("Top Match", f"{ranked[0]['semantic_score']:.0%}" if ranked else "—")

    st.markdown('<hr class="hiq-divider">', unsafe_allow_html=True)

    # ── RANKED LIST ───────────────────────────────────────────
    st.markdown('<div class="hiq-label">Ranked Candidates</div>', unsafe_allow_html=True)

    for c in ranked:
        score_pct = int(c["semantic_score"] * 100)
        badge = '<span class="badge-shortlisted">Shortlisted</span>' if c["shortlisted"] else '<span class="badge-rejected">Not Selected</span>'
        bar_width = score_pct

        with st.expander(f"{'#' + str(c['rank'])}  {c['id']}  ·  {score_pct}%"):
            st.progress(score_pct / 100)
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**File** — `{c['filename']}`")
            col_b.markdown(f"**Match Score** — `{c['semantic_score']:.4f}`")
            st.markdown("**Preview**")
            st.code(c.get("raw_text", "")[:700] + "...", language=None)

    st.markdown('<hr class="hiq-divider">', unsafe_allow_html=True)

    # ── DOWNLOAD ─────────────────────────────────────────────
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
    st.download_button(
        "Export Report",
        data=json.dumps(report, indent=2),
        file_name="hireiq_report.json",
        mime="application/json"
    )
