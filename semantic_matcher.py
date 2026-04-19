"""
semantic_matcher.py — 2026 NLP Engine
Upgrade A: Sentence-BERT semantic embeddings
Upgrade C: ATS-style multi-dimensional scoring
"""

import re
import math
from collections import Counter

# ── Skill Keywords Library (200+) ─────────────────────────────────────────────
SKILL_KEYWORDS = {
    "python","java","javascript","typescript","c++","c#","golang","rust","scala",
    "kotlin","swift","ruby","php","r","matlab","bash","shell","sql","nosql",

    "machine learning","deep learning","nlp","natural language processing",
    "computer vision","reinforcement learning","transformer","bert","gpt","llm",
    "large language model","neural network","cnn","rnn","lstm","xgboost","lightgbm",
    "random forest","svm","regression","classification","clustering",
    "feature engineering","model deployment","mlops","rag","fine-tuning",
    "prompt engineering","vector database","embeddings","semantic search",

    "pandas","numpy","scipy","matplotlib","seaborn","plotly",
    "scikit-learn","sklearn","tensorflow","keras","pytorch","hugging face",
    "transformers","spacy","nltk","gensim","sentence-transformers",
    "langchain","llamaindex","openai","anthropic","fastai",
    "tfidf","tf-idf","cosine similarity","word2vec","fasttext",

    "sql","postgresql","mysql","mongodb","redis","cassandra","elasticsearch",
    "spark","hadoop","kafka","airflow","dbt","etl","data pipeline",
    "data warehouse","bigquery","snowflake","redshift","databricks",

    "aws","azure","gcp","docker","kubernetes","terraform","ansible",
    "ci/cd","github actions","jenkins","linux","git","mlflow","kubeflow",

    "flask","django","fastapi","rest api","graphql","microservices",
    "react","vue","angular","node.js","express",

    "communication","leadership","agile","scrum","teamwork",
    "problem solving","analytical","research","stakeholder management",

    "a/b testing","statistics","hypothesis testing","data analysis",
    "data visualization","power bi","tableau","excel","looker",
}


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\-\+#]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str) -> set:
    text_lower = text.lower()
    found = set()
    for kw in SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            found.add(kw)
    return found


# ── Upgrade A: Sentence-BERT Semantic Similarity ──────────────────────────────
def get_sbert_similarity(text_a: str, text_b: str) -> float:
    """
    Uses sentence-transformers (all-MiniLM-L6-v2) to compute
    semantic similarity. Understands MEANING not just keywords.
    e.g. 'built ML pipelines' matches 'machine learning engineer'
    """
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Chunk long texts to fit model context window
        def chunk_text(text, max_chars=3000):
            return text[:max_chars]

        emb_a = model.encode(chunk_text(text_a), convert_to_tensor=True)
        emb_b = model.encode(chunk_text(text_b), convert_to_tensor=True)
        score = float(util.cos_sim(emb_a, emb_b)[0][0])
        return max(0.0, min(score, 1.0))
    except Exception:
        return None  # fallback to TF-IDF


def get_tfidf_similarity(text_a: str, text_b: str) -> float:
    """TF-IDF cosine similarity fallback."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                              max_features=8000, sublinear_tf=True)
        mat = vec.fit_transform([preprocess(text_a), preprocess(text_b)])
        return float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
    except Exception:
        return _manual_cosine(text_a, text_b)


def _manual_cosine(a: str, b: str) -> float:
    def tf(t): w = t.split(); n = len(w) or 1; return {x: c/n for x, c in Counter(w).items()}
    va, vb = tf(preprocess(a)), tf(preprocess(b))
    vocab = set(va) | set(vb)
    u = [va.get(w, 0) for w in vocab]
    v = [vb.get(w, 0) for w in vocab]
    dot = sum(x*y for x, y in zip(u, v))
    mag = math.sqrt(sum(x**2 for x in u)) * math.sqrt(sum(x**2 for x in v))
    return dot / mag if mag else 0.0


# ── Upgrade C: ATS Multi-Dimensional Scoring ──────────────────────────────────
def compute_semantic_score(
    resume_text: str,
    jd_text: str,
    use_sbert: bool = True,
    use_tfidf_fallback: bool = True,
    skill_boost: float = 0.25,
) -> dict:
    """
    Returns a dict of scores:
      - semantic: SBERT or TF-IDF similarity
      - skill:    keyword overlap ratio
      - final:    weighted combination
    """
    # Semantic score
    semantic_score = None
    method = "tfidf"

    if use_sbert:
        semantic_score = get_sbert_similarity(resume_text, jd_text)
        if semantic_score is not None:
            method = "sbert"

    if semantic_score is None and use_tfidf_fallback:
        semantic_score = get_tfidf_similarity(resume_text, jd_text)

    if semantic_score is None:
        semantic_score = 0.0

    # Skill score
    jd_skills = extract_keywords(jd_text)
    res_skills = extract_keywords(resume_text)
    skill_score = len(jd_skills & res_skills) / len(jd_skills) if jd_skills else semantic_score

    # Final blended score
    final = (1 - skill_boost) * semantic_score + skill_boost * skill_score

    return {
        "semantic": round(min(semantic_score, 1.0), 4),
        "skill":    round(min(skill_score, 1.0), 4),
        "final":    round(min(final, 1.0), 4),
        "method":   method,
    }


def extract_skill_gaps(resume_text: str, jd_text: str) -> tuple:
    jd_skills  = extract_keywords(jd_text)
    res_skills = extract_keywords(resume_text)
    matched = sorted(jd_skills & res_skills)
    gaps    = sorted(jd_skills - res_skills)
    return matched, gaps
