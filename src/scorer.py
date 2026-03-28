import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.embedder import embed_texts

def build_jd_text(jd: dict) -> str:
    if "raw_text" in jd:
        return jd["raw_text"]
    required = ", ".join(jd.get("required_skills", []))
    preferred = ", ".join(jd.get("preferred_skills", []))
    return (
        f"Job Title: {jd.get('title', '')}. "
        f"Required skills: {required}. Preferred skills: {preferred}. "
        f"{jd.get('description', '')}"
    )

def score_resumes(resumes: list[dict], jd: dict) -> list[dict]:
    """Embed JD and all resumes, compute cosine similarity scores."""
    jd_text = build_jd_text(jd)
    resume_texts = [r["raw_text"] for r in resumes]

    print("  🧠 Embedding JD and resumes...")
    all_texts = [jd_text] + resume_texts
    embeddings = embed_texts(all_texts)

    jd_vec = embeddings[0].reshape(1, -1)
    resume_vecs = embeddings[1:]

    similarities = cosine_similarity(jd_vec, resume_vecs)[0]

    scored = []
    for i, resume in enumerate(resumes):
        scored.append({
            **resume,
            "semantic_score": round(float(similarities[i]), 4)
        })

    return scored
