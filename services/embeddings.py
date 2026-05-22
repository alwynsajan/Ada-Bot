import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text, chunk_size=600, overlap=100):
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def generate_embedding(text):
    return model.encode(text).tolist()


def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)

    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))