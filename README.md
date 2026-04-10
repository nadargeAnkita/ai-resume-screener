# 🤖 AI Resume Screener – NLP-Based Job Matching System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-TF--IDF-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> An intelligent, NLP-powered resume screening tool that automatically parses resumes and ranks candidates against job descriptions using **TF-IDF Vectorization** and **Cosine Similarity** — replacing manual shortlisting with a smart, automated workflow.

🔗 **Live Demo:** [https://ai-resume-screener-jhotatkbiapynbkz7k9srs.streamlit.app/](https://ai-resume-screener-jhotatkbiapynbkz7k9srs.streamlit.app/)

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Author](#author)

---

## 📌 About the Project

Recruiters spend hours manually reading resumes to find the right candidate. This project solves that problem by building an **AI-powered resume screening system** that:

- Accepts multiple resumes in **PDF, DOCX, or TXT** format
- Parses and extracts key information from each resume
- Matches each resume against a given **Job Description (JD)**
- Ranks all candidates by their **match score**
- Highlights **skill gaps** — skills required by the JD but missing in the resume
- Exports results as a **CSV file** for sharing with the hiring team

This tool is built entirely using **open-source libraries** — no API keys, no paid services, no internet required after installation.

---

## ✨ Features

- 📄 **Multi-format Resume Parsing** — supports PDF, DOCX, and TXT files
- 🧠 **TF-IDF Vectorization** — converts text into meaningful numerical vectors
- 📐 **Cosine Similarity Scoring** — measures how closely a resume matches the JD
- 🎯 **Skill Keyword Boost** — 200+ curated tech and soft skills for accurate matching
- ❌ **Skill Gap Analysis** — identifies missing skills per candidate
- 🏆 **Candidate Ranking** — automatically ranks all uploaded resumes
- 📊 **Visual Score Charts** — bar charts and donut charts for each candidate
- 💾 **CSV Export** — download ranked results for your team
- ⚙️ **Adjustable Settings** — tune minimum score, skill boost weight, and top-N candidates
- 🌐 **Deployed on Streamlit Cloud** — accessible from any browser, anywhere

---

## 🛠 Tech Stack

| Category | Technology |
|---|---|
| Frontend / UI | Streamlit |
| NLP / Vectorization | scikit-learn (TfidfVectorizer) |
| Similarity Scoring | Cosine Similarity (sklearn) |
| PDF Parsing | pdfplumber, PyPDF2, PyMuPDF |
| DOCX Parsing | python-docx |
| Data Handling | pandas, numpy |
| Visualization | Plotly |
| Deployment | Streamlit Community Cloud |
| Version Control | Git, GitHub |

---

## 📂 Project Structure

```
ai-resume-screener/
│
├── app.py                  # Main Streamlit application — UI and logic
├── matcher.py              # Core NLP engine — TF-IDF + Cosine Similarity
├── resume_parser.py        # Resume text parser — name, email, phone, skills
├── utils.py                # File readers — PDF and DOCX extraction
├── requirements.txt        # All Python dependencies
└── README.md               # Project documentation
```

---

## 🧠 How It Works

### Step 1 — File Upload & Text Extraction
The recruiter uploads one or more resumes (PDF/DOCX/TXT). The `utils.py` module extracts raw text from each file using **pdfplumber** (primary), **PyPDF2** (fallback), and **PyMuPDF** (second fallback) for PDFs, and **python-docx** for Word files.

### Step 2 — Resume Parsing
The `resume_parser.py` module reads the raw text and extracts structured fields:
- **Name** — heuristic detection from the first few lines
- **Email** — regex pattern matching
- **Phone** — digit pattern matching
- **Education** — lines containing degree keywords (B.Tech, M.Tech, PhD, etc.)
- **Years of Experience** — pattern matching ("5 years of experience")

### Step 3 — TF-IDF Vectorization
Both the **Job Description** and each **Resume** are preprocessed (lowercased, punctuation removed, stop words filtered) and fed into `sklearn.TfidfVectorizer`:

```
TF  = (Number of times term appears in document) / (Total terms in document)
IDF = log(Total documents / Documents containing the term)
TF-IDF = TF × IDF
```

Configuration used:
- `ngram_range=(1, 2)` — captures bigrams like "machine learning"
- `sublinear_tf=True` — log-normalization prevents common words from dominating
- `stop_words='english'` — removes noise words like "the", "and", "is"

### Step 4 — Cosine Similarity
Both documents are converted into high-dimensional TF-IDF vectors. Cosine similarity measures the angle between them:

```
Cosine Similarity = (A · B) / (|A| × |B|)

Score = 1.0  →  Identical documents
Score = 0.0  →  Completely unrelated documents
```

### Step 5 — Skill Keyword Boost
A library of **200+ curated skills** (Python, NLP, Docker, SQL, PyTorch, React, etc.) is scanned in both the JD and the resume. The overlap ratio is calculated and blended with the TF-IDF score:

```
Skill Score  = Matched Skills / Total JD Skills
Final Score  = (1 - boost_weight) × TF-IDF Score + boost_weight × Skill Score
```

### Step 6 — Skill Gap Analysis
```
Matched Skills = JD Skills  ∩  Resume Skills   → shown as green tags
Skill Gaps     = JD Skills  −  Resume Skills   → shown as red tags
```

### Step 7 — Ranking & Display
All candidates are sorted by Final Score (descending), filtered by minimum score threshold, and displayed as interactive cards with charts, skill tags, and a downloadable CSV report.

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/nadargeAnkita/ai-resume-screener.git

# 2. Navigate to the project folder
cd ai-resume-screener

# 3. Create a virtual environment
python -m venv venv

# 4. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 5. Install all dependencies
pip install -r requirements.txt

# 6. Run the app
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 🚀 Usage

1. **Paste the Job Description** in the left text box
2. **Upload Resumes** — select PDF, DOCX, or TXT files (multiple files allowed)
3. **Adjust Settings** in the sidebar:
   - Minimum Match Score — filter out low-scoring candidates
   - Show Top N Candidates — limit how many results to display
   - Skill Boost Weight — control how much skill keywords influence the score
4. Click **"🚀 Run Analysis"**
5. View **ranked candidates** with match scores, skill tags, and charts
6. Click **"⬇️ Download Results CSV"** to export for your team

---

## ☁️ Deployment

This project is deployed on **Streamlit Community Cloud** for free.

### Deploy your own copy:

1. Fork this repository
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your forked repo, branch `main`, file `app.py`
5. Click **"Deploy"**

Your app will be live in 2–3 minutes at a public URL.

---



## 👩‍💻 Author

**Ankita Nadarge**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/ankita-nadarge/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/nadargeAnkita)

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and distribute.

---

⭐ **If you found this project helpful, please give it a star on GitHub!**
