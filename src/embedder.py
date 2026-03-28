import os
import numpy as np
from google import genai

def get_gemini_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            with open(".env") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY"):
                        key = line.strip().split("=", 1)[1].strip().strip('"')
        return key

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings using Google Gemini (new google-genai package)."""
    client = genai.Client(api_key=get_gemini_key())
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings

def embed_texts(texts: list[str], batch_size: int = 8) -> np.ndarray:
    """Embed texts in batches to stay within rate limits."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)
    return np.array(all_embeddings)
