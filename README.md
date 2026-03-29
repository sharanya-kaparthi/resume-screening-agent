HireIQ — AI Resume Screening Agent

Screen smarter. Hire faster.

HireIQ is an AI-powered resume screening agent that automatically parses, scores, and ranks candidates against a job description — cutting manual screening time from hours to seconds.
Built for the Product Space AI Agent Hackathon.

The Problem
Hiring teams review dozens — sometimes hundreds — of resumes for every role. Most candidates don't match the core requirements, yet each resume still demands human attention. This is a drain on recruiter time and a bottleneck in the entire hiring pipeline.

What HireIQ Does

Paste or upload a job description
Upload resumes in PDF, DOCX, or TXT format
HireIQ semantically scores each resume against the role
Get a ranked shortlist with match percentages in under 30 seconds
Export the results as a structured JSON report

How It Works
Job Description + Resumes
          ↓
    [ Parser ]         → Extracts raw text from PDF / DOCX / TXT
          ↓
    [ Embedder ]       → Generates semantic vectors via Google Gemini
          ↓
    [ Scorer ]         → Computes cosine similarity against JD
          ↓
    [ Ranker ]         → Sorts candidates, applies shortlist threshold
          ↓
    Ranked Results + Export Report

Project structure
resume-screening-agent/
├── src/
│   ├── parser.py        # Resume & JD text extraction
│   ├── embedder.py      # Google Gemini embedding calls
│   ├── scorer.py        # Cosine similarity scoring
│   ├── ranker.py        # Candidate ranking & shortlisting
│   └── agent.py         # CLI pipeline runner
├── app.py               # Streamlit UI
├── requirements.txt
├── .env.example
└── .gitignore

