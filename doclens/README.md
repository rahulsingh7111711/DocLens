# 🔍 DocLens

**AI-powered document analysis system** — upload PDFs, Word docs, images or text files and ask questions in plain English. Answers are grounded in your document using RAG (Retrieval-Augmented Generation) via Groq + LLaMA3.

---

## Features

- Upload PDF, DOCX, TXT, or scanned image files
- Semantic Q&A — ask any question, get accurate answers from your document
- Automatic document summarisation
- Source chunk references shown for every answer
- Fast retrieval using FAISS vector database
- Powered by Groq (free API tier available)

---

## Project Structure

```
doclens/
├── backend/
│   └── main.py          ← FastAPI server (all API endpoints)
├── frontend/
│   └── app.py           ← Streamlit UI
├── utils/
│   ├── extractor.py     ← Text extraction (PDF, DOCX, OCR)
│   ├── preprocessor.py  ← Text cleaning + chunking
│   ├── embedder.py      ← Sentence Transformers + FAISS
│   └── llm.py           ← Groq API integration
├── requirements.txt
├── .env.example
├── setup.bat            ← First-time Windows setup
├── start_backend.bat    ← Start FastAPI
└── start_frontend.bat   ← Start Streamlit
```

---

## Setup on Windows (Step-by-Step)

### Step 1 — Install Python

1. Go to **https://www.python.org/downloads/**
2. Download **Python 3.11** (recommended)
3. Run the installer
4. ⚠️ **IMPORTANT**: Check **"Add Python to PATH"** before clicking Install

Verify: open Command Prompt and type:
```
python --version
```
You should see `Python 3.11.x`

---

### Step 2 — Install Tesseract OCR (for scanned PDFs/images)

1. Go to: **https://github.com/UB-Mannheim/tesseract/wiki**
2. Download the Windows installer (tesseract-ocr-w64-setup-*.exe)
3. Run the installer — **keep the default install path**: `C:\Program Files\Tesseract-OCR`
4. During installation, select **"Add to PATH"** if prompted

Verify: open a new Command Prompt and type:
```
tesseract --version
```

---

### Step 3 — Get Your Free Groq API Key

1. Go to **https://console.groq.com**
2. Sign up for a free account
3. Click **"API Keys"** → **"Create API Key"**
4. Copy the key (starts with `gsk_...`)

---

### Step 4 — Run Setup

1. Download / clone this project folder
2. Double-click **`setup.bat`**
3. Wait for it to finish (3–5 minutes for first install)

---

### Step 5 — Add Your API Key

1. Open the `.env` file in Notepad (it was created by setup.bat)
2. Replace `your_groq_api_key_here` with your actual key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```
3. Save the file

---

### Step 6 — Run the App

You need **two terminal windows** running simultaneously:

**Terminal 1 — Backend:**
Double-click `start_backend.bat`
→ You should see: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 — Frontend:**
Double-click `start_frontend.bat`
→ Your browser will open automatically at `http://localhost:8501`

---

## How to Use

1. Open **http://localhost:8501** in your browser
2. Click **"Browse files"** in the sidebar → upload a PDF, DOCX, or TXT
3. Click **"Upload & Process"** — wait for chunking/embedding to complete
4. Type a question in the chat box at the bottom
5. Get your answer with source references!

Switch to the **"Summarise"** tab to generate a full document summary.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Check if backend is running |
| POST | /upload | Upload and ingest a document |
| POST | /query | Ask a question |
| POST | /summarise | Summarise a document |
| GET | /documents | List all ingested documents |
| DELETE | /documents/{id} | Remove a document |

Interactive API docs: **http://localhost:8000/docs**

---

## Troubleshooting

**"Backend offline" shown in sidebar**
→ Make sure `start_backend.bat` is running. Check the terminal for errors.

**"No text could be extracted"**
→ If it's a scanned PDF, ensure Tesseract is installed correctly.

**Groq API error**
→ Check your `.env` file has the correct `GROQ_API_KEY`.

**`python` not recognised**
→ Reinstall Python and make sure "Add Python to PATH" was checked.

**Slow first upload**
→ Normal! The Sentence Transformer model downloads on first use (~90 MB).

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend API | FastAPI + Uvicorn |
| Text extraction | pdfplumber, PyPDF2, python-docx, Tesseract |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector search | FAISS |
| LLM | Groq (LLaMA3-8B) |
