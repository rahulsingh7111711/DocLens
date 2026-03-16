"""
Embedding generation and FAISS vector store management.
"""
import os
import pickle
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load model once at module level (cached after first load)
_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Convert a list of text strings into L2-normalised embedding vectors.
    Returns a float32 numpy array of shape (N, dim).
    """
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # L2-normalise so cosine similarity == dot product
    faiss.normalize_L2(embeddings.astype(np.float32))
    return embeddings.astype(np.float32)


def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Build an in-memory FAISS inner-product (cosine) index."""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def search_index(
    index: faiss.IndexFlatIP,
    query_embedding: np.ndarray,
    chunks: List[str],
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Retrieve the top-k most relevant chunks for a query embedding.

    Returns:
        List of (chunk_text, similarity_score) tuples.
    """
    query = query_embedding.reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(query)
    scores, indices = index.search(query, min(top_k, index.ntotal))
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            results.append((chunks[idx], float(score)))
    return results
