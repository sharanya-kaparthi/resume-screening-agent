import os
import time
import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def get_embeddings(texts: list[str], retries: int = 3) -> list[list[float]]:
    """Get embeddings from HuggingFace. Retries on model cold-start (503)."""
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBED_MODEL}"

    for attempt in range(retries):
        response = requests.post(url, headers=HEADERS, json={
            "inputs": texts,
            "options": {"wait_for_model": True}
        })

        if response.status_code == 200:
            return response.json()

        if response.status_code == 503:
            wait = 20 * (attempt + 1)
            print(f"  ⏳ Model loading, retrying in {wait}s...")
            time.sleep(wait)
        else:
            response.raise_for_status()

    raise RuntimeError("HuggingFace embedding model failed after retries.")

def embed_texts(texts: list[str], batch_size: int = 8) -> np.ndarray:
    """Embed texts in batches to avoid API limits."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)
    return np.array(all_embeddings)
