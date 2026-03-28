import os
import time
import requests
import numpy as np

def get_hf_key() -> str:
    try:
        import streamlit as st
        return st.secrets["HF_API_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("HF_API_KEY")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings(texts: list[str], retries: int = 5) -> list[list[float]]:
    HF_API_KEY = get_hf_key()
    HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

    # ✅ New correct endpoint
    url = f"https://api-inference.huggingface.co/models/{EMBED_MODEL}"

    for attempt in range(retries):
        response = requests.post(url, headers=HEADERS, json={
            "inputs": texts,
            "options": {"wait_for_model": True}
        })

        if response.status_code == 200:
            result = response.json()
            # New API returns nested list — flatten if needed
            if isinstance(result[0][0], list):
                result = [r[0] for r in result]
            return result

        if response.status_code in (503, 429):
            wait = 20 * (attempt + 1)
            print(f"⏳ Model loading or rate limited, retrying in {wait}s...")
            time.sleep(wait)
        else:
            response.raise_for_status()

    raise RuntimeError("HuggingFace embedding model failed after retries.")

def embed_texts(texts: list[str], batch_size: int = 8) -> np.ndarray:
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)
    return np.array(all_embeddings)
