import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from resume_parser import parse_resume
from matcher import compute_match_score, extract_skill_gaps
from utils import extract_text_from_pdf, extract_text_from_docx
import io

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --bg-dark: #0f172a;
    --bg-card: #1e293b;
    --bg-card2: #162032;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --border: #334155;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text);
}

.stApp { background: linear-gradient(135deg, #0f172a 0%, #1a1f35 50%, #0f172a 100%); }

h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; }

.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #a78bfa, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}

.hero-sub {
    color: var(--text-muted);
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.score-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
}

.score-high { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.score-mid  { background: #431407; color: #fb923c; border: 1px solid #9a3412; }
.score-low  { background: #450a0a; color: #f87171; border: 1px solid #991b1b; }

.skill-tag {
    display: inline-block;
    background: #1e3a5f;
    color: #7dd3fc;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}

.skill-gap-tag {
    display: inline-block;
    background: #3b1515;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}

.skill-match-tag {
    display: inline-block;
    background: #052e16;
    color: #86efac;
    border: 1px solid #14532d;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}

.candidate-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s;
}

.rank-badge {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    margin-right: 10px;
}

.rank-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #000; }
.rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: #000; }
.rank-3 { background: linear-gradient(135deg, #a16207, #b45309); color: #fff; }
.rank-other { background: #1e293b; color: var(--text-muted); border: 1px solid var(--border); }

.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

div[data-testid="stFileUploader"] {
    background: #162032;
    border: 2px dashed #334155;
    border-radius: 12px;
    padding: 1rem;
}

div[data-testid="stTextArea"] textarea {
    background: #162032 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace;
}

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.03em;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(99,102,241,0.4) !important;
}

.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #10b981) !important; }

hr { border-color: var(--border) !important; }

.stSidebar { background: #0d1626 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    min_score = st.slider("Minimum Match Score (%)", 0, 100, 30)
    top_n = st.slider("Show Top N Candidates", 1, 20, 10)

    st.markdown("---")
    st.markdown("### 🧠 Algorithm")
    use_tfidf = st.checkbox("TF-IDF Vectorization", value=True)
    use_skills = st.checkbox("Skill Extraction Boost", value=True)
    boost_weight = st.slider("Skill Boost Weight", 0.0, 1.0, 0.3)

    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    <small style='color:#64748b'>
    Uses TF-IDF + Cosine Similarity to rank resumes against a Job Description.
    Skill gap analysis highlights missing keywords.
    </small>
    """, unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown('<div class="hero-title">🤖 AI Resume Screener</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">NLP-powered candidate ranking · TF-IDF · Cosine Similarity · Skill Gap Analysis</div>', unsafe_allow_html=True)

st.markdown("---")

# ─── Input Section ────────────────────────────────────────────────────────────
col_jd, col_res = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown('<div class="section-header">📋 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste the Job Description here",
        height=260,
        placeholder="e.g. We are looking for a Python developer with experience in machine learning, NLP, TF-IDF, scikit-learn, REST APIs...",
        label_visibility="collapsed"
    )

with col_res:
    st.markdown('<div class="section-header">📁 Upload Resumes</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded")
        for f in uploaded_files:
            st.markdown(f"<small style='color:#64748b'>📄 {f.name}</small>", unsafe_allow_html=True)

st.markdown("")
col_btn, col_clear = st.columns([2, 8])
with col_btn:
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
with col_clear:
    if st.button("🗑️ Clear Results"):
        st.session_state.results = []
        st.rerun()

# ─── Run Analysis ─────────────────────────────────────────────────────────────
if run_btn:
    if not jd_text.strip():
        st.warning("⚠️ Please paste a Job Description.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, file in enumerate(uploaded_files):
            status.markdown(f"<small>Parsing **{file.name}**...</small>", unsafe_allow_html=True)
            progress.progress((i + 1) / len(uploaded_files))

            # Extract text
            if file.name.endswith(".pdf"):
                raw_text = extract_text_from_pdf(file)
            elif file.name.endswith(".docx"):
                raw_text = extract_text_from_docx(file)
            else:
                raw_text = file.read().decode("utf-8", errors="ignore")

            if not raw_text.strip():
                st.warning(f"⚠️ **{file.name}** — could not extract text. This is likely a scanned/image PDF. Please export it as a text-based PDF from Word/Google Docs and re-upload.")
                continue

            # Parse + score
            parsed = parse_resume(raw_text)
            score, tfidf_score = compute_match_score(
                raw_text, jd_text,
                use_tfidf=use_tfidf,
                skill_boost=boost_weight if use_skills else 0.0
            )
            matched, gaps = extract_skill_gaps(raw_text, jd_text)

            results.append({
                "name": file.name.replace(".pdf","").replace(".docx","").replace(".txt",""),
                "file": file.name,
                "score": round(score * 100, 1),
                "tfidf_score": round(tfidf_score * 100, 1),
                "text": raw_text,
                "parsed": parsed,
                "matched_skills": matched,
                "skill_gaps": gaps,
            })

        status.empty()
        progress.empty()

        # Sort & filter
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        results = [r for r in results if r["score"] >= min_score][:top_n]
        st.session_state.results = results

# ─── Display Results ──────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    st.markdown("---")

    # ── Summary Metrics
    avg_score = sum(r["score"] for r in results) / len(results)
    top_score = results[0]["score"]
    high_fit = sum(1 for r in results if r["score"] >= 70)

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, f"{len(results)}", "Candidates Ranked", "#6366f1"),
        (m2, f"{top_score}%", "Top Match Score", "#10b981"),
        (m3, f"{avg_score:.1f}%", "Avg Match Score", "#f59e0b"),
        (m4, f"{high_fit}", "High Fit (≥70%)", "#a78bfa"),
    ]
    for col, val, label, color in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Score Distribution Chart
    st.markdown('<div class="section-header">📊 Score Distribution</div>', unsafe_allow_html=True)
    df = pd.DataFrame(results)

    colors = []
    for s in df["score"]:
        if s >= 70: colors.append("#10b981")
        elif s >= 45: colors.append("#f59e0b")
        else: colors.append("#ef4444")

    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df["score"],
        marker_color=colors,
        text=df["score"].apply(lambda x: f"{x}%"),
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color="#e2e8f0"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        xaxis=dict(gridcolor="#1e293b", title=""),
        yaxis=dict(gridcolor="#1e293b", title="Match Score (%)", range=[0, 115]),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Ranked Candidates
    st.markdown('<div class="section-header">🏆 Ranked Candidates</div>', unsafe_allow_html=True)

    for i, r in enumerate(results):
        rank = i + 1
        score = r["score"]
        badge_class = {1:"rank-1",2:"rank-2",3:"rank-3"}.get(rank,"rank-other")

        if score >= 70:   score_class, score_emoji = "score-high", "🟢"
        elif score >= 45: score_class, score_emoji = "score-mid",  "🟡"
        else:             score_class, score_emoji = "score-low",  "🔴"

        with st.expander(f"#{rank}  {r['name']}   —   {score_emoji} {score}%", expanded=(rank==1)):

            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**File:** `{r['file']}`")
                st.markdown(f"**TF-IDF Score:** `{r['tfidf_score']}%`")
                st.progress(int(score))

                # Parsed info
                p = r["parsed"]
                if p.get("email"):    st.markdown(f"📧 `{p['email']}`")
                if p.get("phone"):    st.markdown(f"📞 `{p['phone']}`")
                if p.get("name"):     st.markdown(f"👤 `{p['name']}`")

            with c2:
                # Radar-style skill score (simple donut)
                fig2 = go.Figure(go.Pie(
                    values=[score, 100 - score],
                    hole=0.72,
                    marker_colors=["#6366f1","#1e293b"],
                    textinfo="none",
                ))
                fig2.add_annotation(text=f"{score}%", x=0.5, y=0.5,
                    font=dict(size=22, family="JetBrains Mono", color="#e2e8f0"),
                    showarrow=False)
                fig2.update_layout(
                    showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                    paper_bgcolor="rgba(0,0,0,0)", height=140
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Matched skills
            if r["matched_skills"]:
                st.markdown("**✅ Matched Skills:**")
                tags = " ".join(f'<span class="skill-match-tag">{s}</span>' for s in r["matched_skills"])
                st.markdown(tags, unsafe_allow_html=True)

            # Skill gaps
            if r["skill_gaps"]:
                st.markdown("**❌ Skill Gaps (Missing from Resume):**")
                tags = " ".join(f'<span class="skill-gap-tag">{s}</span>' for s in r["skill_gaps"])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.success("No significant skill gaps detected!")

    # ── Export CSV
    st.markdown("---")
    st.markdown('<div class="section-header">💾 Export Results</div>', unsafe_allow_html=True)
    export_df = pd.DataFrame([{
        "Rank": i+1,
        "Candidate": r["name"],
        "File": r["file"],
        "Match Score (%)": r["score"],
        "TF-IDF Score (%)": r["tfidf_score"],
        "Matched Skills": ", ".join(r["matched_skills"]),
        "Skill Gaps": ", ".join(r["skill_gaps"]),
    } for i, r in enumerate(results)])

    csv = export_df.to_csv(index=False).encode()
    st.download_button("⬇️ Download Results CSV", csv, "screening_results.csv", "text/csv")
    st.dataframe(export_df, use_container_width=True, hide_index=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color:#334155;">
        <div style="font-size:4rem; margin-bottom:1rem;">📂</div>
        <div style="font-size:1.2rem; font-weight:600; color:#475569;">No Results Yet</div>
        <div style="color:#334155; margin-top:0.5rem;">Upload resumes and paste a job description to begin screening</div>
    </div>
    """, unsafe_allow_html=True)
