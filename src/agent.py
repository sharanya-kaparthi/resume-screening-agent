import sys
from src.parser import load_all_resumes, parse_job_description
from src.scorer import score_resumes
from src.ranker import rank_candidates
from src.report import save_report, print_summary

def run(job_description_path: str, resumes_folder: str = "data/resumes", top_n: int = 5):
    print(f"\n🚀 Resume Screening Agent Starting...")
    print(f"   JD       : {job_description_path}")
    print(f"   Resumes  : {resumes_folder}")
    print(f"   Shortlist: Top {top_n}\n")

    # Step 1 — Parse
    print("📂 Step 1: Parsing resumes...")
    resumes = load_all_resumes(resumes_folder)
    if not resumes:
        print("❌ No resumes found. Add files to data/resumes/")
        return

    jd = parse_job_description(job_description_path)
    print(f"   Job: {jd.get('title', 'Loaded')}")

    # Step 2 — Score
    print("\n📊 Step 2: Scoring against job description...")
    scored = score_resumes(resumes, jd)

    # Step 3 — Rank
    print("\n🏆 Step 3: Ranking candidates...")
    ranked = rank_candidates(scored, top_n=top_n)

    # Step 4 — Report
    print("\n📝 Step 4: Generating report...")
    save_report(ranked, jd)
    print_summary(ranked)

if __name__ == "__main__":
    jd_path = sys.argv[1] if len(sys.argv) > 1 else "data/jobs/job.txt"
    run(jd_path)
