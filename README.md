# 🚀 AI Resume Screener — Semantic Job Matching System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Sentence-BERT](https://img.shields.io/badge/Sentence--BERT-Semantic_NLP-8b5cf6?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3-10b981?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> A production-grade, AI-powered resume screening system using **Sentence-BERT semantic embeddings**, **Groq LLaMA 3 LLM analysis**, and **ATS-style multi-dimensional scoring** — built for the 2026 job market.

🔗 **Live Demo:** [https://nadargeankita-ai-resume-screener-app-exlbc2.streamlit.app/](https://nadargeankita-ai-resume-screener-app-exlbc2.streamlit.app/)

---

## Why This Project Stands Out

Traditional resume screeners use TF-IDF keyword matching — a technique from 2010. This project uses the same technology stack that modern ATS platforms and AI hiring tools use in 2026:

| Old Approach | This Project |
|---|---|
| TF-IDF keyword matching | Sentence-BERT semantic embeddings |
| Exact keyword comparison | Understands meaning and context |
| Single score | ATS-style multi-dimensional scoring |
| No explanation | LLM-generated fit reports |
| Manual interviews | Auto-generated tailored interview questions |
| No candidate feedback | AI-powered resume improvement tips |

---

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Usage](#usage)
- [Deployment](#deployment)
- [Security](#security)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Live Demo

🔗 **[https://ai-resume-screener-jhotatkbiapynbkz7k9srs.streamlit.app](https://ai-resume-screener-jhotatkbiapynbkz7k9srs.streamlit.app)**

You can try the live demo directly in your browser — no installation required.
Upload any resume PDF or DOCX and paste a job description to see the AI screening in action.

---

## Features

- 🧠 **Sentence-BERT Semantic Matching** — Uses the `all-MiniLM-L6-v2` transformer model to convert resumes and job descriptions into 384-dimensional semantic vectors. Understands meaning, not just keywords. "Built ML pipelines" correctly matches "machine learning engineer" even without shared words.

- 📐 **ATS Multi-Dimensional Scoring** — Three separate scores computed per candidate: Semantic Score (BERT similarity), Skill Score (keyword overlap from 200+ skill library), and Final blended score. Displayed as progress bars and radar charts — exactly how real ATS systems work.

- 🤖 **LLM Fit Report (Groq LLaMA 3)** — AI-generated structured candidate assessment that explains WHY a candidate scored X%, lists key strengths, highlights areas of concern, and gives a hiring recommendation (Strong Hire / Hire / Maybe / No Hire).

- ❓ **Interview Questions Generator** — Automatically generates 6 tailored questions per candidate: 2 technical, 2 behavioral, and 2 gap-probing questions — all specific to the JD and candidate's background.

- 💡 **Resume Improvement Tips** — 5 specific, actionable suggestions telling candidates exactly what skills, certifications, or projects to add to score higher for this specific role.

- 📄 **Multi-format Resume Parsing** — Supports PDF, DOCX, and TXT with triple-fallback extraction: pdfplumber → PyPDF2 → PyMuPDF. Handles both text-based and complex formatted PDFs.

- 📊 **Rich Visualizations** — Grouped bar charts comparing all candidates, individual donut charts per candidate, and radar charts showing multi-dimensional score breakdown using Plotly.

- 🔒 **Secure API Key Handling** — API key is never shown in the UI. Loaded securely from `.env` file locally or Streamlit Secrets on deployment. Never exposed to users or pushed to GitHub.

- 💾 **CSV Export** — Download complete ranked results including all scores, matched skills, and skill gaps as a CSV file for sharing with your hiring team.

- ⚙️ **Fully Configurable** — Tune the semantic engine, skill boost weight, minimum score filter, and top-N candidates from the sidebar without touching any code.

---

## Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| Semantic NLP | Sentence-BERT (`all-MiniLM-L6-v2`) | Semantic embeddings and similarity |
| LLM Analysis | Groq API (LLaMA 3.3 70B) | Fit reports, interview questions, tips |
| Fallback NLP | scikit-learn TF-IDF | Keyword-based fallback scoring |
| Frontend / UI | Streamlit | Web interface |
| PDF Parsing | pdfplumber, PyPDF2, PyMuPDF | Resume text extraction |
| DOCX Parsing | python-docx | Word document extraction |
| Data Handling | pandas, numpy | Data processing and export |
| Visualization | Plotly | Charts and graphs |
| Secret Management | python-dotenv | Secure API key loading |
| Deployment | Streamlit Community Cloud | Free cloud hosting |
| Version Control | Git, GitHub | Source control |

---

## Project Structure

```
ai-resume-screener/
│
├── app.py                  # Main Streamlit UI — layout, logic, results display
├── semantic_matcher.py     # Sentence-BERT + TF-IDF scoring engine
├── llm_analyzer.py         # Groq LLaMA 3 — fit reports, questions, tips
├── resume_parser.py        # Extracts name, email, phone, education from text
├── utils.py                # PDF and DOCX file readers with triple fallback
├── requirements.txt        # All Python dependencies
├── .env.example            # Template for environment variables
├── .gitignore              # Prevents .env and secrets from going to GitHub
└── README.md               # Project documentation
```

---

## How It Works

### Step 1 — File Upload and Text Extraction (`utils.py`)

The recruiter uploads one or more resumes in PDF, DOCX, or TXT format. The extraction engine tries three libraries in order until text is successfully extracted:

```
PDF uploaded
    → Try pdfplumber (best for standard PDFs)
    → Try PyPDF2 (fallback for older PDFs)
    → Try PyMuPDF/fitz (fallback for complex layouts)
    → If all fail → warn user (scanned/image PDF)

DOCX uploaded
    → python-docx reads paragraphs and table cells
```

### Step 2 — Resume Parsing (`resume_parser.py`)

Extracts structured information from raw text using regex patterns:

```
Name         → First 1-5 lines where all words start with capital letter
Email        → Standard email regex pattern
Phone        → Digit and punctuation pattern matching
Education    → Lines containing: B.Tech, M.Tech, PhD, MBA, Bachelor, Master, etc.
Experience   → Patterns like "5 years of experience" or "3+ yrs experience"
Skills       → Matched against 200+ keyword library from semantic_matcher.py
```

### Step 3 — Sentence-BERT Semantic Matching (`semantic_matcher.py`)

This is the core upgrade over traditional TF-IDF. The `all-MiniLM-L6-v2` model converts entire sentences into 384-dimensional dense vectors that capture semantic meaning:

```
Traditional TF-IDF:
"Developed machine learning pipelines"  vs  "ML model deployment experience"
→ Score: ~0.05 (almost no shared words)

Sentence-BERT:
"Developed machine learning pipelines"  vs  "ML model deployment experience"
→ Score: ~0.78 (same concept, understood semantically)
```

The model is downloaded once (~90MB) on first run and cached locally.

### Step 4 — ATS Multi-Dimensional Scoring

Three scores are computed per candidate:

```
Semantic Score = cosine_similarity(SBERT(JD), SBERT(Resume))
              = measures contextual and semantic alignment

Skill Score    = |JD_skills ∩ Resume_skills| / |JD_skills|
              = measures keyword/technology overlap

Final Score    = (1 - boost_weight) × Semantic + boost_weight × Skill
              = weighted combination (default: 75% semantic, 25% skill)
```

### Step 5 — Groq LLM Analysis (`llm_analyzer.py`)

Three AI-powered analyses are generated per candidate using Groq's free LLaMA 3.3 70B model:

**Fit Report:**
```
Input:  JD + Resume + Match Scores
Output: Overall Assessment + Key Strengths + Areas of Concern + Hiring Recommendation
```

**Interview Questions:**
```
Input:  JD + Resume
Output: 2 Technical + 2 Behavioral + 2 Gap-Probing questions
```

**Resume Tips:**
```
Input:  JD + Resume + Skill Gaps list
Output: 5 specific actionable improvements for this exact role
```

### Step 6 — Skill Gap Analysis

```
Matched Skills = JD_skills ∩ Resume_skills  →  shown as green tags ✅
Skill Gaps     = JD_skills − Resume_skills  →  shown as red tags ❌
```

The skill library covers 200+ technologies including Python, NLP, Docker, SQL, PyTorch, React, Kubernetes, AWS, and many more.

### Step 7 — Ranking and Display

All candidates are sorted by Final Score in descending order, filtered by the minimum score threshold, and displayed as interactive expandable cards. Each card has 4 tabs: ATS Score, Fit Report, Interview Questions, and Resume Tips.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/nadargeAnkita/ai-resume-screener.git

# 2. Navigate into the project folder
cd ai-resume-screener

# 3. Create a virtual environment
python -m venv venv

# 4. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# 5. Install all dependencies
pip install -r requirements.txt

# Note: First run downloads the Sentence-BERT model (~90MB)
# This happens once and is cached automatically

# 6. Set up your environment file (see Environment Setup below)

# 7. Run the app
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## Environment Setup

### Getting a Free Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up with your Google account — completely free, no credit card needed
3. Click **API Keys** in the left sidebar
4. Click **Create API Key** and give it a name
5. Copy the key — it starts with `gsk_`

### Setting Up the .env File (Local)

```bash
# Copy the example file
cp .env.example .env

# Open .env and add your key
GROQ_API_KEY=gsk_your_actual_key_here
```

The `.env` file is listed in `.gitignore` so it will never be pushed to GitHub.

### Setting Up Secrets (Streamlit Cloud)

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click your deployed app
3. Click **Settings** → **Secrets**
4. Add the following:

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```

5. Click **Save** — Streamlit injects it automatically at runtime

---

## Usage

1. Open the app at `http://localhost:8501` (local) or the deployed URL
2. **Paste the Job Description** in the left text panel
3. **Upload resumes** — select PDF, DOCX, or TXT files (multiple files allowed simultaneously)
4. **Adjust settings** in the sidebar if needed:
   - Min Match Score — filters out low-scoring candidates
   - Top N Candidates — limits how many results are shown
   - Skill Boost Weight — controls the influence of skill keywords vs semantic score
5. Click **Run Analysis**
6. For each candidate, explore 4 tabs:
   - **ATS Score** — multi-dimensional score breakdown with radar chart and skill tags
   - **Fit Report** — AI-generated assessment with hiring recommendation
   - **Interview Questions** — 6 tailored questions ready to use
   - **Resume Tips** — actionable suggestions for the candidate
7. Click **Download Results CSV** to export for your hiring team

---

## Deployment

This project is deployed on **Streamlit Community Cloud** for free.

### Deploy your own copy

```
1. Fork this repository on GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your forked repo, branch: main, file: app.py
5. Click "Deploy"
6. After deployment: Settings → Secrets → add GROQ_API_KEY
```

Your app will be live in 2-3 minutes at a public URL you can share on your resume and LinkedIn.

---

## Security

This project follows security best practices for API key management:

- API key is never shown in the app UI — no input box exposed to users
- Key is loaded from `.env` file locally using `python-dotenv`
- Key is loaded from Streamlit Secrets on cloud deployment
- `.env` is listed in `.gitignore` — never pushed to GitHub
- `.env.example` is provided as a safe template (contains no real keys)
- `secrets.toml` is also listed in `.gitignore` for local Streamlit testing

---

## Future Improvements

- [ ] spaCy NER for better structured candidate info extraction
- [ ] RAG-based JD understanding using Pinecone or ChromaDB vector database
- [ ] Batch processing via ZIP upload for large candidate pools
- [ ] Automated candidate email notifications for shortlisted applicants
- [ ] Multi-language resume support using multilingual BERT
- [ ] Integration with ATS platforms like Workday and Greenhouse via API
- [ ] Candidate comparison side-by-side view
- [ ] Historical screening data dashboard with trends

---

## Author

**Ankita Nadarge**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/ankita-nadarge)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/nadargeAnkita)

---

## License

This project is licensed under the MIT License — feel free to use, modify, and distribute with attribution.

---

⭐ **If you found this project helpful, please give it a star on GitHub — it helps others discover it!**
