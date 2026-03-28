def rank_candidates(scored_resumes: list[dict], top_n: int = 10) -> list[dict]:
    """Sort by semantic score and return top N candidates."""
    ranked = sorted(scored_resumes, key=lambda x: x["semantic_score"], reverse=True)
    
    for i, candidate in enumerate(ranked):
        candidate["rank"] = i + 1
        candidate["shortlisted"] = i < top_n

    return ranked

def get_shortlisted(ranked: list[dict]) -> list[dict]:
    return [c for c in ranked if c["shortlisted"]]
