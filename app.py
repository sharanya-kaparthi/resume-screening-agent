import streamlit as st
import tempfile, os, json
from src.parser import parse_resume, parse_job_description
from src.scorer import score_resumes
from src.ranker import rank_candidates

st.set_page_config(page_title="HireIQ", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
    --bg:        #f5f5f7;
    --surface:   rgba(255,255,255,0.72);
    --surface2:  rgba(255,255,255,0.55);
    --border:    rgba(0,0,0,0.07);
    --text:      #1d1d1f;
    --subtext:   #6e6e73;
    --accent:    #0071e3;
    --accent-h:  #0077ed;
    --success:   #34c759;
    --radius:    18px;
    --radius-sm: 12px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* ── HIDE CHROME ── */
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
#MainMenu, footer { display: none !important; visibility: hidden !important; }

[data-testid="stSidebar"] { display: none !important; }

.main .block-container {
    max-width: 860px !important;
    padding: 0 1.5rem 6rem 1.5rem !important;
    margin: 0 auto !important;
}

/* ── HERO ── */
.hiq-hero {
    text-align: center;
    padding: 5.5rem 0 4rem 0;
    animation: fadeUp 0.8s cubic-bezier(.22,1,.36,1) both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hiq-wordmark {
    font-family: 'DM Serif Display', serif;
    font-size: 4.2rem;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: var(--text);
    line-height: 1;
}
.hiq-wordmark em {
    font-style: italic;
    color: var(--accent);
}
.hiq-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: var(--subtext);
    margin-top: 0.65rem;
    letter-spacing: 0.01em;
}

/* ── GLASS CARD ── */
/* Use isolation instead of overflow:hidden so backdrop-filter works */
.hiq-card {
    background: var(--surface);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 2px 24px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.3s ease;
    isolation: isolate;
}
.hiq-card:hover {
    box-shadow: 0 4px 32px rgba(0,0,0,0.09), 0 1px 4px rgba(0,0,0,0.06);
}
.hiq-card-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--subtext);
    margin-bottom: 1.1rem;
}

/* Staggered card animation */
.hiq-card:nth-child(1) { animation: fadeUp 0.7s 0.05s cubic-bezier(.22,1,.36,1) both; }
.hiq-card:nth-child(2) { animation: fadeUp 0.7s 0.15s cubic-bezier(.22,1,.36,1) both; }
.hiq-card:nth-child(3) { animation: fadeUp 0.7s 0.25s cubic-bezier(.22,1,.36,1) both; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.12) !important;
    outline: none !important;
    background: #fff !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #b0b0b5 !important;
    font-weight: 300 !important;
}
/* Hide default labels (use label_visibility="collapsed" in Python too) */
.stTextInput label,
.stTextArea label { display: none !important; }

/* ── TABS ── */
/* Updated selectors for current Streamlit versions */
.stTabs [role="tablist"] {
    background: rgba(0,0,0,0.05) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border-bottom: none !important;
    margin-bottom: 1.25rem !important;
}
.stTabs [role="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--subtext) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.1rem !important;
    border: none !important;
    transition: all 0.18s ease !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: var(--text) !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1) !important;
}
/* Remove the default bottom-border indicator Streamlit adds */
.stTabs [role="tab"][aria-selected="true"]::after,
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
    background: rgba(255,255,255,0.5) !important;
    border: 1.5px dashed rgba(0,0,0,0.14) !important;
    border-radius: var(--radius-sm) !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"] > section:hover {
    border-color: var(--accent) !important;
    background: rgba(0,113,227,0.03) !important;
}
[data-testid="stFileUploader"] > section > div {
    color: var(--subtext) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
}
/* Hide the outer label that Streamlit auto-generates for file uploader */
[data-testid="stFileUploader"] > label { display: none !important; }

/* ── BUTTON ── */
/* Scope full-width only to the main CTA, not buttons inside columns */
[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] .stButton > button {
    width: auto !important;
}
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 980px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.75rem 2.2rem !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 2px 12px rgba(0,113,227,0.28) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: var(--accent-h) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,113,227,0.36) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: rgba(0,113,227,0.08) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(0,113,227,0.2) !important;
    border-radius: 980px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: background 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,113,227,0.14) !important;
}

/* ── SLIDER ── */
/* Correct selector path for Streamlit slider track fill */
[data-testid="stSlider"] [data-testid="stThumbValue"],
[data-testid="stSlider"] [role="slider"] {
    color: var(--accent) !important;
}
[data-testid="stSlider"] > div > div > div:nth-child(2) > div {
    background: var(--accent) !important;
}
.stSlider label,
[data-testid="stSlider"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--subtext) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 1.35rem 1.5rem !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--subtext) !important;
}
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2rem !important;
    color: var(--text) !important;
    line-height: 1.1 !important;
}
/* Remove the metric delta arrow if unused */
[data-testid="stMetricDelta"] { display: none !important; }

/* ── EXPANDER ── */
details > summary,
[data-testid="stExpander"] summary {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    padding: 1rem 1.25rem !important;
    transition: background 0.2s !important;
    margin-bottom: 0.5rem !important;
    list-style: none !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(255,255,255,0.9) !important;
}
[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.6) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    padding: 1.25rem !important;
}

/* ── PROGRESS ── */
[data-testid="stProgressBar"] > div {
    background: rgba(0,0,0,0.06) !important;
    border-radius: 99px !important;
    height: 4px !important;
    overflow: hidden !important;
}
[data-testid="stProgressBar"] > div > div {
    background: var(--accent) !important;
    border-radius: 99px !important;
}

/* ── STATUS ── */
[data-testid="stStatusWidget"],
.stStatus {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── ALERT — keep borders for accessibility, just restyle ── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    border-left-width: 3px !important;   /* keep left indicator, drop full border */
    border-top: none !important;
    border-right: none !important;
    border-bottom: none !important;
}

/* ── CAPTION ── */
[data-testid="stCaptionContainer"],
.stCaption {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    color: var(--subtext) !important;
}

/* ── CODE BLOCK ── */
[data-testid="stCode"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
}

/* ── SECTION TITLE ── */
.hiq-section {
    font-family: 'DM Serif Display', serif;
    font-size: 1.55rem;
    font-weight: 400;
    color: var(--text);
    margin: 2.5rem 0 1rem 0;
    letter-spacing: -0.01em;
}

/* ── COLUMN GAP FIX — Streamlit adds overflow:hidden to col wrappers ── */
[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 1rem !important;
}
[data-testid="column"] {
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hiq-hero">
    <div class="hiq-wordmark">Hire<em>IQ</em></div>
    <div class="hiq-sub">Screen smarter. Hire faster.</div>
</div>
""", unsafe_allow_html=True)

# ── JOB DESCRIPTION ──────────────────────────────────────────
# NOTE: Streamlit strips unclosed HTML tags injected via st.markdown.
# Wrap content in a single self-contained div per st.markdown call.
st.markdown('<div class="hiq-card"><div class="hiq-card-label">Role</div></div>',
            unsafe_allow_html=True)

with st.container():
    jd_tab1, jd_tab2 = st.tabs(["Write", "Upload"])
    jd_dict = None

    with jd_tab1:
        job_title = st.text_input(
            "title",
            placeholder="Job title  —  e.g. Senior Product Designer",
            label_visibility="collapsed"
        )
        jd_input = st.text_area(
            "jd",
            height=150,
            placeholder="Describe the role — skills required, responsibilities, experience level...",
            label_visibility="collapsed"
        )
        if jd_input.strip():
            jd_dict = {"title": job_title.strip() or "Open Role", "raw_text": jd_input.strip()}

    with jd_tab2:
        jd_file = st.file_uploader(
            "Upload job description",
            type=["txt", "json"],
            label_visibility="collapsed"
        )
        if jd_file:
            with tempfile.NamedTemporaryFile(delete=False,
                    suffix=os.path.splitext(jd_file.name)[-1]) as tmp:
                tmp.write(jd_file.read())
            try:
                jd_dict = parse_job_description(tmp.name)
                st.success(f"Loaded — {jd_file.name}")
            except Exception as e:
                st.error(str(e))

# ── RESUMES ───────────────────────────────────────────────────
st.markdown('<div class="hiq-card"><div class="hiq-card-label">Candidates</div></div>',
            unsafe_allow_html=True)

with st.container():
    uploaded_resumes = st.file_uploader(
        "Drop resumes here",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_resumes:
        st.caption(f"{len(uploaded_resumes)} resume{'s' if len(uploaded_resumes) > 1 else ''} ready to screen")

# ── CONTROLS ─────────────────────────────────────────────────
col_a, col_b = st.columns([1, 2])
with col_a:
    top_n = st.slider("Shortlist size", 1, 20, 5)
with col_b:
    # Push button down to align with slider vertically
    st.markdown("<div style='padding-top: 1.75rem;'></div>", unsafe_allow_html=True)
    run_btn = st.button("Screen Candidates →", use_container_width=True)

# ── PIPELINE ─────────────────────────────────────────────────
if run_btn:
    if not jd_dict:
        st.error("Add a job description before screening.")
        st.stop()
    if not uploaded_resumes:
        st.error("Upload at least one resume to get started.")
        st.stop()

    resumes = []
    with st.status("Reading resumes…", expanded=False) as status:
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
                st.write(f"Skipped {f.name}: {e}")
        status.update(
            label=f"{len(resumes)} resume{'s' if len(resumes) > 1 else ''} parsed",
            state="complete"
        )

    if not resumes:
        st.error("No resumes could be read. Try plain text or PDF files.")
        st.stop()

    with st.status("Analysing fit…", expanded=False) as status:
        try:
            scored = score_resumes(resumes, jd_dict)
            status.update(label="Analysis complete", state="complete")
        except Exception as e:
            st.error(f"Something went wrong during scoring: {e}")
            st.stop()

    ranked = rank_candidates(scored, top_n=top_n)
    shortlisted = [c for c in ranked if c["shortlisted"]]
    not_selected = [c for c in ranked if not c["shortlisted"]]

    # ── OVERVIEW ─────────────────────────────────────────────
    st.markdown('<div class="hiq-section">Results</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Screened", len(ranked))
    m2.metric("Shortlisted", len(shortlisted))
    m3.metric("Not Selected", len(not_selected))
    m4.metric("Top Match", f"{ranked[0]['semantic_score']:.0%}" if ranked else "—")

    # ── SHORTLISTED ───────────────────────────────────────────
    st.markdown('<div class="hiq-section">Shortlisted</div>', unsafe_allow_html=True)
    if shortlisted:
        for c in shortlisted:
            score_pct = int(c["semantic_score"] * 100)
            with st.expander(f"#{c['rank']}  ·  {c['id']}  ·  {score_pct}% match  ✦"):
                st.progress(score_pct / 100)
                col1, col2 = st.columns(2)
                col1.markdown(f"**File** &nbsp; `{c['filename']}`")
                col2.markdown(f"**Score** &nbsp; `{c['semantic_score']:.4f}`")
                st.markdown("**Resume excerpt**")
                st.code(c.get("raw_text", "")[:600] + "…", language=None)
    else:
        st.info("No candidates met the shortlist threshold. Try lowering the shortlist size.")

    # ── NOT SELECTED ──────────────────────────────────────────
    if not_selected:
        st.markdown('<div class="hiq-section">Not Selected</div>', unsafe_allow_html=True)
        for c in not_selected:
            score_pct = int(c["semantic_score"] * 100)
            with st.expander(f"#{c['rank']}  ·  {c['id']}  ·  {score_pct}% match"):
                st.progress(score_pct / 100)
                col1, col2 = st.columns(2)
                col1.markdown(f"**File** &nbsp; `{c['filename']}`")
                col2.markdown(f"**Score** &nbsp; `{c['semantic_score']:.4f}`")

    # ── EXPORT ───────────────────────────────────────────────
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    report = {
        "job_title": jd_dict.get("title"),
        "total_screened": len(ranked),
        "shortlisted": len(shortlisted),
        "ranked_candidates": [
            {
                "rank": c["rank"],
                "name": c["id"],
                "score": c["semantic_score"],
                "shortlisted": c["shortlisted"]
            }
            for c in ranked
        ]
    }
    st.download_button(
        "↓  Export Screening Report",
        data=json.dumps(report, indent=2),
        file_name="hireiq_report.json",
        mime="application/json"
    )
