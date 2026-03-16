"""
Text preprocessing and chunking utilities.
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean extracted text:
    - Collapse multiple blank lines
    - Remove non-printable characters
    - Normalize whitespace
    """
    # Remove non-printable characters (keep newlines and tabs)
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]', ' ', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping word-based chunks.

    Args:
        text: Cleaned input text.
        chunk_size: Approximate number of words per chunk.
        overlap: Number of words to overlap between adjacent chunks.

    Returns:
        List of text chunk strings.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap  # slide forward with overlap

    return chunks
