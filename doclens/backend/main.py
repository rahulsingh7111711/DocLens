"""
DocLens FastAPI Backend
-----------------------
Endpoints:
  POST /upload      — ingest a document into the RAG pipeline
  POST /query       — ask a question against an ingested document
  POST /summarise   — generate a structured summary
  GET  /health      — liveness check
  GET  /documents   — list all ingested documents
"""
import os
import sys
import time
import uuid
from typing import Dict, List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure utils package is importable when running from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.extractor import extract_text
from utils.preprocessor import clean_text, chunk_text
from utils.embedder import embed_texts, build_index, search_index
from utils.llm import generate_answer, generate_summary

app = FastAPI(
    title="DocLens API",
    description="AI-powered document analysis with RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory document store ──────────────────────────────────────────────────
# Structure: { doc_id: { "filename", "chunks", "index" } }
DOC_STORE: Dict[str, dict] = {}


# ── Request / Response Models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    doc_id: str
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    source_chunks: List[str]
    latency_ms: float
    doc_id: str


class SummariseRequest(BaseModel):
    doc_id: str


class SummariseResponse(BaseModel):
    summary: str
    doc_id: str
    filename: str


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    status: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "documents_loaded": len(DOC_STORE)}


@app.get("/documents", response_model=List[DocumentInfo])
def list_documents():
    return [
        DocumentInfo(
            doc_id=doc_id,
            filename=data["filename"],
            chunk_count=len(data["chunks"]),
        )
        for doc_id, data in DOC_STORE.items()
    ]


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    allowed_types = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_types)}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large. Max size is 50 MB.")

    # Extract text
    try:
        raw_text = extract_text(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Text extraction failed: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this document. If it is a scanned PDF, ensure Tesseract is installed.",
        )

    # Preprocess and chunk
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, chunk_size=500, overlap=50)

    # Embed and index
    embeddings = embed_texts(chunks)
    index = build_index(embeddings)

    # Store in memory
    doc_id = str(uuid.uuid4())
    DOC_STORE[doc_id] = {
        "filename": file.filename,
        "chunks": chunks,
        "index": index,
    }

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        chunk_count=len(chunks),
        status="success",
    )


@app.post("/query", response_model=QueryResponse)
def query_document(req: QueryRequest):
    if req.doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail=f"Document '{req.doc_id}' not found. Please upload it first.")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    start = time.time()
    doc = DOC_STORE[req.doc_id]

    # Embed query and retrieve
    query_emb = embed_texts([req.query])
    results = search_index(doc["index"], query_emb[0], doc["chunks"], top_k=req.top_k)

    context_chunks = [chunk for chunk, _ in results]

    # Generate answer
    answer = generate_answer(req.query, context_chunks)
    latency_ms = (time.time() - start) * 1000

    return QueryResponse(
        answer=answer,
        source_chunks=context_chunks,
        latency_ms=round(latency_ms, 1),
        doc_id=req.doc_id,
    )


@app.post("/summarise", response_model=SummariseResponse)
def summarise_document(req: SummariseRequest):
    if req.doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail=f"Document '{req.doc_id}' not found.")

    doc = DOC_STORE[req.doc_id]
    summary = generate_summary(doc["chunks"])

    return SummariseResponse(
        summary=summary,
        doc_id=req.doc_id,
        filename=doc["filename"],
    )


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    if doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    del DOC_STORE[doc_id]
    return {"status": "deleted", "doc_id": doc_id}
