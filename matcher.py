"""
matcher.py  –  Core NLP matching engine
Implements TF-IDF vectorization + Cosine Similarity for resume-to-JD scoring.
"""

import re
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─── Skill Keywords Library ───────────────────────────────────────────────────
SKILL_KEYWORDS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "scala", "kotlin", "swift", "ruby", "php", "r", "matlab", "bash", "shell",

    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "transformer", "bert", "gpt",
    "llm", "neural network", "cnn", "rnn", "lstm", "xgboost", "lightgbm",
    "random forest", "svm", "regression", "classification", "clustering",
    "feature engineering", "model deployment", "mlops",

    # Data Science
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch",
    "hugging face", "transformers", "spacy", "nltk", "gensim",
    "tfidf", "tf-idf", "cosine similarity", "word2vec", "fasttext",

    # Data Engineering
    "sql", "nosql", "postgresql", "mysql", "mongodb", "redis", "cassandra",
    "elasticsearch", "spark", "hadoop", "kafka", "airflow", "dbt",
    "etl", "data pipeline", "data warehouse", "bigquery", "snowflake",
    "redshift", "databricks",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins", "linux", "git", "mlflow",

    # Web / Backend
    "flask", "django", "fastapi", "rest api", "graphql", "microservices",
    "react", "vue", "angular", "node.js", "express",

    # Soft skills / domain
    "communication", "leadership", "agile", "scrum", "teamwork",
    "problem solving", "analytical", "research",
}


def preprocess(text: str) -> str:
    """Lowercase, remove punctuation, normalize whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s\-\+#]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str) -> set:
    """Extract known skill keywords from text."""
    text_lower = text.lower()
    found = set()
    for kw in SKILL_KEYWORDS:
        # Match whole-word or phrase
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            found.add(kw)
    return found


def compute_match_score(
    resume_text: str,
    jd_text: str,
    use_tfidf: bool = True,
    skill_boost: float = 0.3,
) -> tuple[float, float]:
    """
    Returns (final_score, tfidf_score) both in [0, 1].

    Algorithm:
    1. TF-IDF Vectorization on [jd, resume]
    2. Cosine similarity → tfidf_score
    3. Skill keyword overlap → skill_score
    4. final = (1 - skill_boost) * tfidf_score + skill_boost * skill_score
    """
    r_clean = preprocess(resume_text)
    j_clean = preprocess(jd_text)

    # ── TF-IDF Cosine Similarity
    if use_tfidf:
        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=8000,
                sublinear_tf=True,
            )
            tfidf_matrix = vectorizer.fit_transform([j_clean, r_clean])
            tfidf_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception:
            tfidf_score = 0.0
    else:
        tfidf_score = _manual_cosine(j_clean, r_clean)

    # ── Skill Overlap Score
    jd_skills   = extract_keywords(jd_text)
    res_skills  = extract_keywords(resume_text)

    if jd_skills:
        matched = jd_skills & res_skills
        skill_score = len(matched) / len(jd_skills)
    else:
        skill_score = tfidf_score  # fallback

    # ── Weighted Combination
    if skill_boost > 0:
        final_score = (1 - skill_boost) * tfidf_score + skill_boost * skill_score
    else:
        final_score = tfidf_score

    return min(final_score, 1.0), min(tfidf_score, 1.0)


def extract_skill_gaps(resume_text: str, jd_text: str) -> tuple[list, list]:
    """
    Returns:
        matched_skills  : skills present in both JD and resume
        skill_gaps      : skills required by JD but missing in resume
    """
    jd_skills  = extract_keywords(jd_text)
    res_skills = extract_keywords(resume_text)

    matched = sorted(jd_skills & res_skills)
    gaps    = sorted(jd_skills - res_skills)
    return matched, gaps


# ─── Manual Cosine (fallback without sklearn) ─────────────────────────────────
def _manual_cosine(text_a: str, text_b: str) -> float:
    """Pure-python TF cosine similarity (fallback)."""
    def tf(text):
        words = text.split()
        total = len(words) or 1
        return {w: c / total for w, c in Counter(words).items()}

    a, b = tf(text_a), tf(text_b)
    vocab = set(a) | set(b)
    vec_a = [a.get(w, 0) for w in vocab]
    vec_b = [b.get(w, 0) for w in vocab]

    dot   = sum(x * y for x, y in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(x**2 for x in vec_a))
    mag_b = math.sqrt(sum(x**2 for x in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
