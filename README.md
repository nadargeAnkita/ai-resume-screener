# 🤖 AI Resume Screener – NLP-Based Job Matching System

> Automatically rank resumes against a Job Description using TF-IDF vectorization, Cosine Similarity, and Skill Gap Analysis.

---

## 📂 Project Structure

```
resume_screener/
├── app.py              # Streamlit UI – main entry point
├── matcher.py          # Core NLP engine (TF-IDF + Cosine Similarity)
├── resume_parser.py    # Resume text parser (name, email, phone, skills)
├── utils.py            # File readers (PDF, DOCX)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🧠 How It Works (Full Explanation)

### 1. `utils.py` – File Extraction
- Accepts PDF, DOCX, and TXT files uploaded via Streamlit
- Uses **pdfplumber** (primary) or **PyPDF2** (fallback) to extract PDF text
- Uses **python-docx** to read DOCX paragraphs and tables

### 2. `resume_parser.py` – Structured Parsing
- Extracts **name** (heuristic: first capitalised multi-word line)
- Extracts **email** via regex
- Extracts **phone** via regex
- Extracts **education** (lines containing degree keywords)
- Extracts **years of experience** via regex patterns
- Uses the SKILL_KEYWORDS library from matcher.py to list detected skills

### 3. `matcher.py` – Core NLP Engine

#### TF-IDF (Term Frequency – Inverse Document Frequency)
- **TF** = how often a term appears in a document
- **IDF** = how rare a term is across all documents
- TF-IDF assigns high weights to important, specific terms
- We use `sklearn.TfidfVectorizer` with:
  - `ngram_range=(1,2)` → captures bigrams like "machine learning"
  - `sublinear_tf=True` → log-normalization of term frequencies
  - `stop_words='english'` → removes noise words

#### Cosine Similarity
- Converts JD and Resume into TF-IDF vectors
- Measures the angle between them: score = 1 means identical, 0 means completely different
- Formula: `cos(θ) = (A · B) / (|A| × |B|)`

#### Skill Keyword Boost
- 200+ curated tech/soft skills in `SKILL_KEYWORDS`
- Calculates overlap ratio: `matched_skills / jd_skills`
- Blended score: `final = (1 - boost) × tfidf_score + boost × skill_score`

#### Skill Gap Analysis
- `matched_skills` = JD skills ∩ Resume skills
- `skill_gaps` = JD skills − Resume skills (what the candidate is missing)

### 4. `app.py` – Streamlit Interface
- Left panel: paste Job Description
- Right panel: multi-file uploader (PDF, DOCX, TXT)
- Sidebar: tune algorithm settings (boost weight, min score, top-N)
- Results: ranked cards, donut charts, skill tags, CSV export

---

## 🚀 Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch app
streamlit run app.py
```

Open: http://localhost:8501

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. Push this folder to a **GitHub repository**
2. Go to https://share.streamlit.io → "New app"
3. Select your repo, branch (`main`), and file (`app.py`)
4. Click **Deploy** → get a public URL instantly

### Alternative: Deploy to Hugging Face Spaces
1. Create a Space at https://huggingface.co/spaces
2. Select **Streamlit** as SDK
3. Upload all files (app.py, matcher.py, resume_parser.py, utils.py, requirements.txt)
4. Spaces auto-builds and gives you a public URL

---

## 🧪 How to Use

1. **Paste the Job Description** in the left text box
2. **Upload resumes** (multiple PDFs/DOCXs allowed)
3. Click **"🚀 Run Analysis"**
4. View ranked candidates with:
   - Match Score (%) – blended TF-IDF + skill boost
   - Donut chart visual per candidate
   - Matched skills (green tags)
   - Skill gaps (red tags)
5. **Download CSV** for sharing with your team

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| Vectorization | scikit-learn TfidfVectorizer |
| Similarity | Cosine Similarity (sklearn) |
| PDF Parsing | pdfplumber, PyPDF2 |
| DOCX Parsing | python-docx |
| Charts | Plotly |
| Data | pandas |

---

## 📈 Future Improvements

- Named Entity Recognition (NER) with spaCy for better name/company extraction
- Sentence-BERT for semantic similarity (beyond keyword matching)
- Multi-lingual support
- ATS scoring rubric (location, salary, visa)
- Database integration for persistent candidate tracking
