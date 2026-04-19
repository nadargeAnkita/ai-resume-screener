import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import extract_text_from_pdf, extract_text_from_docx
from resume_parser import parse_resume
from semantic_matcher import compute_semantic_score, extract_skill_gaps
from llm_analyzer import generate_fit_report, generate_interview_questions, generate_resume_tips

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screener 2026",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #6366f1;
    --secondary: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg: #0a0f1e;
    --card: #111827;
    --card2: #1a2236;
    --border: #1f2d45;
    --text: #e2e8f0;
    --muted: #64748b;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); }
.stApp { background: linear-gradient(135deg, #0a0f1e 0%, #111827 100%); }

.hero { text-align: center; padding: 2rem 0 1.5rem 0; }
.hero-badge { display: inline-block; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 4px 14px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1rem; }
.hero-title { font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #e2e8f0, #a78bfa, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1.2; margin-bottom: 0.5rem; }
.hero-sub { color: var(--muted); font-size: 1rem; }

.section-label { font-size: 0.72rem; font-weight: 600; color: var(--primary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }

.metric-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem; text-align: center; }
.metric-value { font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.metric-label { font-size: 0.75rem; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.score-high { color: #10b981; }
.score-mid  { color: #f59e0b; }
.score-low  { color: #ef4444; }

.tag { display: inline-block; padding: 2px 9px; border-radius: 5px; font-size: 0.75rem; margin: 2px; font-family: 'JetBrains Mono', monospace; border: 1px solid; }
.tag-match { background: #052e16; color: #4ade80; border-color: #14532d; }
.tag-gap   { background: #450a0a; color: #f87171; border-color: #7f1d1d; }
.tag-skill { background: #0c1a3a; color: #7dd3fc; border-color: #1e3a5f; }

.badge-sbert { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 2px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; }
.badge-llm   { background: linear-gradient(135deg, #059669, #0d9488); color: white; padding: 2px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; }

.report-box { background: var(--card2); border: 1px solid var(--border); border-radius: 10px; padding: 1rem 1.2rem; margin-top: 10px; font-size: 0.88rem; line-height: 1.7; color: var(--text); }
.report-box h4 { color: var(--primary); margin-bottom: 6px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.06em; }

.ats-bar-label { font-size: 0.8rem; color: var(--muted); width: 120px; }

div[data-testid="stFileUploader"] { background: #111827; border: 2px dashed #1f2d45; border-radius: 12px; padding: 1rem; }
div[data-testid="stTextArea"] textarea { background: #111827 !important; border: 1px solid #1f2d45 !important; border-radius: 8px; color: var(--text) !important; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

.stButton > button { background: linear-gradient(135deg, #6366f1, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 0.6rem 2rem !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; }
.stButton > button:hover { box-shadow: 0 8px 20px rgba(99,102,241,0.4) !important; }
.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #10b981) !important; }
hr { border-color: var(--border) !important; }
.stSidebar { background: #080d1a !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key in ["results", "api_key"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "results" else ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
def get_api_key() -> str:
    """
    Securely load Groq API key.
    Priority: Streamlit Secrets → .env file → empty string
    Key is NEVER shown in UI or pushed to GitHub.
    """
    # 1. Streamlit Cloud secrets (for deployment)
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    # 2. Local .env file
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        key = os.getenv("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return ""

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    # ── Secure API Key Loading ─────────────────────────────────────────────
    st.markdown("### 🔑 API Key Status")
    api_key = get_api_key()
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ Groq API Key loaded securely")
    else:
        st.session_state.api_key = ""
        st.warning("⚠️ Groq API Key not found")
        st.markdown("""<small style='color:#64748b'>
        To enable LLM features:<br>
        <b>Local:</b> Add <code>GROQ_API_KEY=gsk_...</code> to your <code>.env</code> file<br>
        <b>Deployed:</b> Add to Streamlit → Settings → Secrets
        </small>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎛️ Filters")
    min_score = st.slider("Min Match Score (%)", 0, 100, 20)
    top_n = st.slider("Top N Candidates", 1, 20, 10)

    st.markdown("---")
    st.markdown("### 🧠 Engine")
    use_sbert = st.checkbox("Sentence-BERT Semantic Matching", value=True)
    use_tfidf_fallback = st.checkbox("TF-IDF Fallback (if BERT unavailable)", value=True)
    skill_boost = st.slider("Skill Boost Weight", 0.0, 1.0, 0.25, 0.05)

    st.markdown("---")
    st.markdown("### 📊 LLM Features")
    gen_report = st.checkbox("Generate Fit Report", value=True)
    gen_questions = st.checkbox("Generate Interview Questions", value=True)
    gen_tips = st.checkbox("Resume Improvement Tips", value=True)

    st.markdown("---")
    st.markdown("""<small style='color:#334155'>
    🚀 2026 Edition<br>
    Sentence-BERT + Groq LLaMA 3<br>
    Semantic understanding beyond keywords
    </small>""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">2026 Edition</div>
    <div class="hero-title">AI Resume Screener</div>
    <div class="hero-sub">Sentence-BERT Semantic Matching · LLM Fit Reports · ATS Scoring · Interview Questions Generator</div>
</div>
""", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown('<span class="badge-sbert">Sentence-BERT</span> &nbsp; Semantic embeddings — understands meaning, not just keywords', unsafe_allow_html=True)
with col_b:
    st.markdown('<span class="badge-llm">Groq LLaMA 3</span> &nbsp; AI-generated fit reports, interview questions & resume tips', unsafe_allow_html=True)
with col_c:
    st.markdown('📊 &nbsp; ATS-style multi-dimensional scoring with explainability', unsafe_allow_html=True)

st.markdown("---")

# ── Inputs ────────────────────────────────────────────────────────────────────
col_jd, col_res = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown('<div class="section-label">📋 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("JD", height=280, placeholder="Paste the full job description here...", label_visibility="collapsed")

with col_res:
    st.markdown('<div class="section-label">📁 Upload Resumes (PDF / DOCX / TXT)</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) ready")
        for f in uploaded_files:
            st.markdown(f"<small style='color:#475569'>📄 {f.name}</small>", unsafe_allow_html=True)

st.markdown("")
col_btn, col_clr, _ = st.columns([2, 2, 6])
with col_btn:
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
with col_clr:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.results = []
        st.rerun()

# ── Analysis ──────────────────────────────────────────────────────────────────
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
            status.markdown(f"⚙️ Processing **{file.name}**...")
            progress.progress((i + 1) / len(uploaded_files))

            # Extract text
            if file.name.lower().endswith(".pdf"):
                raw_text = extract_text_from_pdf(file)
            elif file.name.lower().endswith(".docx"):
                raw_text = extract_text_from_docx(file)
            else:
                raw_text = file.read().decode("utf-8", errors="ignore")

            if not raw_text.strip():
                st.warning(f"⚠️ Could not extract text from **{file.name}**. It may be a scanned/image PDF.")
                continue

            # Parse resume
            parsed = parse_resume(raw_text)

            # Semantic scoring
            scores = compute_semantic_score(
                raw_text, jd_text,
                use_sbert=use_sbert,
                use_tfidf_fallback=use_tfidf_fallback,
                skill_boost=skill_boost
            )

            # Skill gap
            matched, gaps = extract_skill_gaps(raw_text, jd_text)

            # LLM Analysis
            llm_report = ""
            llm_questions = ""
            llm_tips = ""

            if st.session_state.api_key:
                if gen_report:
                    status.markdown(f"🤖 Generating fit report for **{file.name}**...")
                    llm_report = generate_fit_report(raw_text, jd_text, scores, st.session_state.api_key)
                if gen_questions:
                    status.markdown(f"🤖 Generating interview questions for **{file.name}**...")
                    llm_questions = generate_interview_questions(raw_text, jd_text, st.session_state.api_key)
                if gen_tips:
                    status.markdown(f"🤖 Generating resume tips for **{file.name}**...")
                    llm_tips = generate_resume_tips(raw_text, jd_text, gaps, st.session_state.api_key)

            results.append({
                "name": file.name.rsplit(".", 1)[0],
                "file": file.name,
                "scores": scores,
                "final_score": round(scores["final"] * 100, 1),
                "parsed": parsed,
                "matched_skills": matched,
                "skill_gaps": gaps,
                "llm_report": llm_report,
                "llm_questions": llm_questions,
                "llm_tips": llm_tips,
            })

        status.empty()
        progress.empty()

        results = sorted(results, key=lambda x: x["final_score"], reverse=True)
        results = [r for r in results if r["final_score"] >= min_score][:top_n]
        st.session_state.results = results

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    st.markdown("---")

    # Metrics
    avg = sum(r["final_score"] for r in results) / len(results)
    high = sum(1 for r in results if r["final_score"] >= 70)
    m1, m2, m3, m4 = st.columns(4)
    for col, val, label, color in [
        (m1, len(results), "Candidates Ranked", "#6366f1"),
        (m2, f"{results[0]['final_score']}%", "Top Score", "#10b981"),
        (m3, f"{avg:.1f}%", "Avg Score", "#f59e0b"),
        (m4, high, "High Fit ≥70%", "#a78bfa"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # Bar chart
    st.markdown('<div class="section-label">📊 Candidate Score Comparison</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{"Candidate": r["name"], "Semantic": round(r["scores"]["semantic"]*100,1), "Skill Match": round(r["scores"]["skill"]*100,1), "Final": r["final_score"]} for r in results])
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Semantic Score", x=df["Candidate"], y=df["Semantic"], marker_color="#6366f1"))
    fig.add_trace(go.Bar(name="Skill Match", x=df["Candidate"], y=df["Skill Match"], marker_color="#10b981"))
    fig.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#64748b"),
        xaxis=dict(gridcolor="#1f2d45"), yaxis=dict(gridcolor="#1f2d45", title="Score (%)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=20, b=20), height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # Candidate Cards
    st.markdown('<div class="section-label">🏆 Ranked Candidates</div>', unsafe_allow_html=True)

    for i, r in enumerate(results):
        rank = i + 1
        score = r["final_score"]
        sc = "score-high" if score >= 70 else "score-mid" if score >= 45 else "score-low"
        emoji = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"

        with st.expander(f"#{rank}  {r['name']}   —   {emoji} {score}%  |  Semantic: {round(r['scores']['semantic']*100,1)}%  |  Skill: {round(r['scores']['skill']*100,1)}%", expanded=(rank==1)):

            tab1, tab2, tab3, tab4 = st.tabs(["📊 ATS Score", "🤖 Fit Report", "❓ Interview Questions", "💡 Resume Tips"])

            # ── Tab 1: ATS Score
            with tab1:
                c1, c2 = st.columns([3, 2])
                with c1:
                    p = r["parsed"]
                    if p.get("name"):  st.markdown(f"👤 **{p['name']}**")
                    if p.get("email"): st.markdown(f"📧 `{p['email']}`")
                    if p.get("phone"): st.markdown(f"📞 `{p['phone']}`")
                    if p.get("experience_years"): st.markdown(f"💼 `{p['experience_years']} years experience`")

                    st.markdown("**ATS Score Breakdown:**")
                    ats = {
                        "Semantic Match": r["scores"]["semantic"],
                        "Skill Overlap": r["scores"]["skill"],
                        "Final Score": r["scores"]["final"],
                    }
                    for label, val in ats.items():
                        pct = round(val * 100)
                        color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 45 else "#ef4444"
                        st.markdown(f"<div style='display:flex;align-items:center;gap:10px;margin:4px 0'><span class='ats-bar-label'>{label}</span><div style='flex:1;background:#1f2d45;border-radius:4px;height:16px;overflow:hidden'><div style='width:{pct}%;background:{color};height:100%;border-radius:4px;display:flex;align-items:center;justify-content:flex-end;padding-right:6px'><span style='font-size:10px;color:white;font-family:JetBrains Mono'>{pct}%</span></div></div></div>", unsafe_allow_html=True)

                    if r["matched_skills"]:
                        st.markdown("**✅ Matched Skills:**")
                        st.markdown(" ".join(f'<span class="tag tag-match">{s}</span>' for s in r["matched_skills"]), unsafe_allow_html=True)
                    if r["skill_gaps"]:
                        st.markdown("**❌ Skill Gaps:**")
                        st.markdown(" ".join(f'<span class="tag tag-gap">{s}</span>' for s in r["skill_gaps"]), unsafe_allow_html=True)

                with c2:
                    fig2 = go.Figure(go.Pie(
                        values=[score, 100-score], hole=0.72,
                        marker_colors=["#6366f1","#1f2d45"], textinfo="none"
                    ))
                    fig2.add_annotation(text=f"{score}%", x=0.5, y=0.5,
                        font=dict(size=20, family="JetBrains Mono", color="#e2e8f0"), showarrow=False)
                    fig2.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                        paper_bgcolor="rgba(0,0,0,0)", height=160)
                    st.plotly_chart(fig2, use_container_width=True)

                    # Radar chart
                    cats = ["Semantic", "Skills", "Overall"]
                    vals = [round(r["scores"]["semantic"]*100), round(r["scores"]["skill"]*100), round(r["scores"]["final"]*100)]
                    fig3 = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself", fillcolor="rgba(99,102,241,0.2)", line=dict(color="#6366f1")))
                    fig3.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0,100], gridcolor="#1f2d45", color="#64748b"), angularaxis=dict(gridcolor="#1f2d45", color="#64748b")),
                        showlegend=False, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)", height=200)
                    st.plotly_chart(fig3, use_container_width=True)

            # ── Tab 2: LLM Fit Report
            with tab2:
                if r["llm_report"]:
                    st.markdown(f'<div class="report-box">{r["llm_report"]}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔑 Add your Anthropic API key in the sidebar to generate an AI-powered fit report for this candidate.")

            # ── Tab 3: Interview Questions
            with tab3:
                if r["llm_questions"]:
                    st.markdown(f'<div class="report-box">{r["llm_questions"]}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔑 Add your Anthropic API key in the sidebar to auto-generate tailored interview questions.")

            # ── Tab 4: Resume Tips
            with tab4:
                if r["llm_tips"]:
                    st.markdown(f'<div class="report-box">{r["llm_tips"]}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔑 Add your Anthropic API key in the sidebar to generate resume improvement suggestions.")

    # Export
    st.markdown("---")
    export_df = pd.DataFrame([{
        "Rank": i+1, "Candidate": r["name"], "File": r["file"],
        "Final Score (%)": r["final_score"],
        "Semantic Score (%)": round(r["scores"]["semantic"]*100, 1),
        "Skill Score (%)": round(r["scores"]["skill"]*100, 1),
        "Matched Skills": ", ".join(r["matched_skills"]),
        "Skill Gaps": ", ".join(r["skill_gaps"]),
    } for i, r in enumerate(results)])
    st.download_button("⬇️ Download Results CSV", export_df.to_csv(index=False).encode(), "results.csv", "text/csv")
    st.dataframe(export_df, use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#1f2d45">
        <div style="font-size:3.5rem;margin-bottom:1rem">🚀</div>
        <div style="font-size:1.1rem;font-weight:600;color:#334155">Ready to Screen</div>
        <div style="color:#1f2d45;margin-top:0.5rem">Paste a JD and upload resumes to begin</div>
    </div>
    """, unsafe_allow_html=True)
