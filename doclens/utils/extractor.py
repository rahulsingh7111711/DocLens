"""
Text extraction utilities for PDF, DOCX, TXT, and image files.
"""
import io
import os
from pathlib import Path

import pdfplumber
import PyPDF2
from docx import Document
from PIL import Image
import pytesseract


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from uploaded file bytes based on file extension.
    Returns extracted text as a string.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(file_bytes)
    elif ext == ".docx":
        return _extract_docx(file_bytes)
    elif ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore")
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return _extract_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(file_bytes: bytes) -> str:
    """Try pdfplumber first, fall back to PyPDF2, then OCR."""
    text = ""

    # Attempt 1: pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages).strip()
    except Exception:
        pass

    # Attempt 2: PyPDF2 fallback
    if not text:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
        except Exception:
            pass

    # Attempt 3: OCR fallback (scanned PDFs)
    if not text:
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(file_bytes)
            ocr_texts = [pytesseract.image_to_string(img) for img in images]
            text = "\n".join(ocr_texts).strip()
        except Exception:
            pass

    return text


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_image(file_bytes: bytes) -> str:
    """Run Tesseract OCR on an image file."""
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)
