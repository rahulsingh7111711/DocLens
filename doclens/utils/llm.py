"""
Groq LLM integration for RAG-grounded answer generation.
"""
import os
from typing import List

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client: Groq = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Please add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


def generate_answer(query: str, context_chunks: List[str]) -> str:
    """
    Send a RAG prompt to Groq and return the generated answer.

    Args:
        query: User's natural language question.
        context_chunks: Retrieved document chunks to use as context.

    Returns:
        LLM-generated answer string.
    """
    context = "\n\n---\n\n".join(context_chunks)

    system_prompt = (
        "You are DocLens, an expert document analysis assistant. "
        "Answer the user's question using ONLY the information provided in the document context below. "
        "If the answer is not found in the context, say: 'I could not find that information in the uploaded document.' "
        "Be concise, accurate, and cite relevant parts of the context when helpful. "
        "Format your response clearly using bullet points or numbered lists where appropriate."
    )

    user_prompt = f"""Document context:
{context}

User question: {query}

Answer:"""

    client = get_client()
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def generate_summary(chunks: List[str]) -> str:
    """
    Generate a structured summary from all document chunks.
    """
    # Use first 20 chunks to stay within context limits
    sample = chunks[:20]
    context = "\n\n---\n\n".join(sample)

    system_prompt = (
        "You are DocLens, a document summarisation assistant. "
        "Produce a clear, structured summary of the document content provided. "
        "Include: 1) A 2-3 sentence overview, 2) Key topics or themes, "
        "3) Important entities, dates, or figures mentioned, "
        "4) Any key conclusions or findings. "
        "Use markdown formatting with headers and bullet points."
    )

    user_prompt = f"""Document content:
{context}

Provide a structured summary:"""

    client = get_client()
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
