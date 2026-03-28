import os
import json

def extract_text_from_pdf(path: str) -> str:
    import pymupdf as fitz
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc).strip()

def extract_text_from_docx(path: str) -> str:
    import docx
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

def extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def parse_resume(path: str) -> dict:
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(path)
    elif ext in (".docx", ".doc"):
        raw_text = extract_text_from_docx(path)
    elif ext in (".txt", ".text"):
        raw_text = extract_text_from_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    filename = os.path.basename(path)
    candidate_id = os.path.splitext(filename)[0]
    return {
        "id": candidate_id,
        "filename": filename,
        "raw_text": raw_text
    }

def parse_job_description(path: str) -> dict:
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".json":
        with open(path) as f:
            return json.load(f)
    elif ext == ".txt":
        with open(path, encoding="utf-8") as f:
            return {"title": "Role", "raw_text": f.read().strip()}
    else:
        raise ValueError(f"Unsupported JD format: {ext}")

def load_all_resumes(folder: str = "data/resumes") -> list[dict]:
    supported = (".pdf", ".docx", ".doc", ".txt")
    resumes = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(supported):
            path = os.path.join(folder, filename)
            try:
                resumes.append(parse_resume(path))
                print(f"  ✅ Parsed: {filename}")
            except Exception as e:
                print(f"  ❌ Failed: {filename} — {e}")
    return resumes
