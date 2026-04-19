"""
llm_analyzer.py — Upgrade B: Groq LLM Integration (FREE)
Uses Groq API with LLaMA 3 model — completely free, no credit card needed.
Get your free API key at: https://console.groq.com

Generates:
  1. Candidate Fit Report — WHY this score, strengths, concerns
  2. Interview Questions — tailored to candidate gaps
  3. Resume Improvement Tips — what to add/fix to score higher
"""


def _call_groq(prompt: str, api_key: str, max_tokens: int = 800) -> str:
    """Call Groq API with LLaMA 3 model — free tier."""
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM Error: {str(e)[:150]}]"


def generate_fit_report(
    resume_text: str,
    jd_text: str,
    scores: dict,
    api_key: str
) -> str:
    """Generate a structured candidate fit report explaining the score."""
    prompt = f"""You are an expert recruiter and talent analyst. Analyze this candidate's resume against the job description and write a concise professional fit report.

JOB DESCRIPTION:
{jd_text[:1500]}

CANDIDATE RESUME:
{resume_text[:1500]}

MATCH SCORES:
- Semantic Match: {round(scores['semantic']*100, 1)}%
- Skill Match: {round(scores['skill']*100, 1)}%
- Overall Score: {round(scores['final']*100, 1)}%

Write a structured fit report with these sections (use HTML formatting with <b> tags for section titles):
1. <b>Overall Assessment</b> — 2-3 sentences on overall fit
2. <b>Key Strengths</b> — 3 bullet points on what matches well
3. <b>Areas of Concern</b> — 2-3 bullet points on gaps or risks
4. <b>Hiring Recommendation</b> — one of: Strong Hire / Hire / Maybe / No Hire — with 1 sentence reason

Keep it concise, professional, and actionable. Use <br> for line breaks and • for bullet points."""

    return _call_groq(prompt, api_key, max_tokens=600)


def generate_interview_questions(
    resume_text: str,
    jd_text: str,
    api_key: str
) -> str:
    """Generate tailored interview questions based on candidate profile and JD gaps."""
    prompt = f"""You are a senior technical recruiter. Based on this candidate's resume and the job description, generate 6 tailored interview questions.

JOB DESCRIPTION:
{jd_text[:1200]}

CANDIDATE RESUME:
{resume_text[:1200]}

Generate exactly 6 interview questions:
- 2 Technical questions (testing specific skills from the JD)
- 2 Behavioral questions (based on role requirements)
- 2 Gap-probing questions (testing areas where the candidate seems weak)

Format each question with HTML like this:
<b>Technical 1:</b> [question]<br>
<b>Technical 2:</b> [question]<br>
<b>Behavioral 1:</b> [question]<br>
<b>Behavioral 2:</b> [question]<br>
<b>Gap Probe 1:</b> [question]<br>
<b>Gap Probe 2:</b> [question]<br>

Make questions specific, insightful, and directly relevant to both the JD and this candidate's background."""

    return _call_groq(prompt, api_key, max_tokens=500)


def generate_resume_tips(
    resume_text: str,
    jd_text: str,
    skill_gaps: list,
    api_key: str
) -> str:
    """Generate actionable resume improvement suggestions for the candidate."""
    gaps_str = ", ".join(skill_gaps[:15]) if skill_gaps else "None identified"

    prompt = f"""You are a professional resume coach. Analyze this candidate's resume against the job description and provide specific, actionable improvement tips.

JOB DESCRIPTION:
{jd_text[:1000]}

CANDIDATE RESUME:
{resume_text[:1000]}

IDENTIFIED SKILL GAPS: {gaps_str}

Provide exactly 5 specific, actionable resume improvement tips to help this candidate score higher for this role.

Format with HTML:
<b>Tip 1:</b> [specific action]<br>
<b>Tip 2:</b> [specific action]<br>
<b>Tip 3:</b> [specific action]<br>
<b>Tip 4:</b> [specific action]<br>
<b>Tip 5:</b> [specific action]<br>

Be specific — mention exact skills, certifications, or project types to add. Not generic advice."""

    return _call_groq(prompt, api_key, max_tokens=400)
