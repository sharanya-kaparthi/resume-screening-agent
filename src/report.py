import json
import os
from datetime import datetime

def save_report(ranked_candidates: list[dict], jd: dict, output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_title = jd.get("title", "role").replace(" ", "_")
    filename = f"{output_dir}/{job_title}_{timestamp}.json"

    report = {
        "job_title": jd.get("title", "Unknown"),
        "screened_at": timestamp,
        "total_candidates": len(ranked_candidates),
        "shortlisted": sum(1 for c in ranked_candidates if c["shortlisted"]),
        "ranked_candidates": [
            {
                "rank": c["rank"],
                "id": c["id"],
                "filename": c["filename"],
                "semantic_score": c["semantic_score"],
                "shortlisted": c["shortlisted"]
            }
            for c in ranked_candidates
        ]
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved → {filename}")
    return filename

def print_summary(ranked_candidates: list[dict]):
    print("\n" + "=" * 55)
    print(f"{'RANK':<6} {'CANDIDATE':<30} {'SCORE':<10} {'STATUS'}")
    print("=" * 55)
    for c in ranked_candidates:
        status = "✅ Shortlisted" if c["shortlisted"] else "❌ Not shortlisted"
        score = f"{c['semantic_score']:.0%}"
        print(f"#{c['rank']:<5} {c['id']:<30} {score:<10} {status}")
    print("=" * 55)
