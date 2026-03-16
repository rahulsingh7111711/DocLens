"""
DocLens — Streamlit Frontend
"""
import time
import requests
import streamlit as st

API_BASE = "http://localhost:8000"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1F4E79;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1rem;
        color: #555;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .answer-box {
        background: #f0f6ff;
        border-left: 4px solid #2E75B6;
        padding: 1.2rem 1.4rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .chunk-box {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #444;
        margin-bottom: 0.5rem;
    }
    .metric-pill {
        display: inline-block;
        background: #e8f4fd;
        color: #1F4E79;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 6px;
    }
    .doc-badge {
        background: #e8f4fd;
        border: 1px solid #b5d4f4;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #1F4E79;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def check_api():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def get_documents():
    try:
        r = requests.get(f"{API_BASE}/documents", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def upload_document(file_bytes, filename):
    try:
        r = requests.post(
            f"{API_BASE}/upload",
            files={"file": (filename, file_bytes)},
            timeout=120,
        )
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500


def query_document(doc_id, query, top_k):
    try:
        r = requests.post(
            f"{API_BASE}/query",
            json={"doc_id": doc_id, "query": query, "top_k": top_k},
            timeout=60,
        )
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500


def summarise_document(doc_id):
    try:
        r = requests.post(
            f"{API_BASE}/summarise",
            json={"doc_id": doc_id},
            timeout=120,
        )
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500


def delete_document(doc_id):
    try:
        r = requests.delete(f"{API_BASE}/documents/{doc_id}", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


# ── Session state init ────────────────────────────────────────────────────────
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 DocLens")
    st.caption("AI Document Analysis")
    st.divider()

    # API status
    api_ok = check_api()
    if api_ok:
        st.success("✅ Backend connected", icon=None)
    else:
        st.error("❌ Backend offline — start the FastAPI server first.")
        st.code("uvicorn backend.main:app --reload", language="bash")

    st.divider()

    # Upload section
    st.markdown("### 📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="PDF, Word, TXT, or image files up to 50 MB",
    )

    if uploaded_file and api_ok:
        if st.button("⬆️ Upload & Process", use_container_width=True):
            with st.spinner("Extracting text, chunking, embedding..."):
                data, status = upload_document(uploaded_file.read(), uploaded_file.name)
            if status == 200:
                st.success(f"✅ Ingested! {data['chunk_count']} chunks created.")
                st.session_state.selected_doc = data["doc_id"]
                st.session_state.chat_history = []
                st.rerun()
            else:
                st.error(f"Upload failed: {data.get('detail', 'Unknown error')}")

    st.divider()

    # Documents list
    st.markdown("### 📂 Ingested Documents")
    docs = get_documents()

    if not docs:
        st.caption("No documents yet. Upload one above.")
    else:
        for doc in docs:
            col1, col2 = st.columns([4, 1])
            with col1:
                label = f"📄 {doc['filename'][:22]}..." if len(doc['filename']) > 25 else f"📄 {doc['filename']}"
                is_selected = st.session_state.selected_doc == doc["doc_id"]
                btn_type = "primary" if is_selected else "secondary"
                if st.button(label, key=f"sel_{doc['doc_id']}", use_container_width=True, type=btn_type):
                    st.session_state.selected_doc = doc["doc_id"]
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{doc['doc_id']}"):
                    delete_document(doc["doc_id"])
                    if st.session_state.selected_doc == doc["doc_id"]:
                        st.session_state.selected_doc = None
                        st.session_state.chat_history = []
                    st.rerun()

    st.divider()
    st.caption("Powered by Groq · FAISS · Sentence Transformers")


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🔍 DocLens</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-powered document analysis — ask questions, get grounded answers.</p>', unsafe_allow_html=True)

if not api_ok:
    st.warning("⚠️ The backend server is not running. Please start it using the command shown in the sidebar.")
    st.stop()

if st.session_state.selected_doc is None:
    st.info("👈 Upload a document from the sidebar to get started.")
    st.stop()

# Find selected doc info
docs = get_documents()
selected_info = next((d for d in docs if d["doc_id"] == st.session_state.selected_doc), None)

if selected_info:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**Active document:** 📄 `{selected_info['filename']}`")
    with col2:
        st.markdown(f'<span class="metric-pill">📦 {selected_info["chunk_count"]} chunks</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="metric-pill">🤖 Groq LLaMA3</span>', unsafe_allow_html=True)

st.divider()

# Tabs
tab1, tab2 = st.tabs(["💬 Ask Questions", "📋 Summarise"])

# ── Tab 1: Q&A ────────────────────────────────────────────────────────────────
with tab1:
    top_k = st.slider("Chunks to retrieve (top-k)", min_value=1, max_value=10, value=5, help="More chunks = broader context, slower response")

    # Chat history
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(entry["question"])
        with st.chat_message("assistant"):
            st.markdown(entry["answer"])
            with st.expander("📎 Source chunks used"):
                for i, chunk in enumerate(entry["source_chunks"], 1):
                    st.markdown(f'<div class="chunk-box"><b>Chunk {i}:</b> {chunk[:400]}{"..." if len(chunk) > 400 else ""}</div>', unsafe_allow_html=True)
            st.caption(f"⚡ {entry['latency_ms']} ms")

    # Input
    if query := st.chat_input("Ask a question about your document..."):
        with st.chat_message("user"):
            st.write(query)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                data, status = query_document(st.session_state.selected_doc, query, top_k)

            if status == 200:
                st.markdown(data["answer"])
                with st.expander("📎 Source chunks used"):
                    for i, chunk in enumerate(data["source_chunks"], 1):
                        st.markdown(f'<div class="chunk-box"><b>Chunk {i}:</b> {chunk[:400]}{"..." if len(chunk) > 400 else ""}</div>', unsafe_allow_html=True)
                st.caption(f"⚡ {data['latency_ms']} ms")

                st.session_state.chat_history.append({
                    "question": query,
                    "answer": data["answer"],
                    "source_chunks": data["source_chunks"],
                    "latency_ms": data["latency_ms"],
                })
            else:
                st.error(f"Query failed: {data.get('detail', 'Unknown error')}")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()


# ── Tab 2: Summarise ──────────────────────────────────────────────────────────
with tab2:
    st.markdown("Generate a structured summary of the entire document.")
    if st.button("✨ Generate Summary", use_container_width=True, type="primary"):
        with st.spinner("Summarising document... this may take 15–30 seconds."):
            data, status = summarise_document(st.session_state.selected_doc)

        if status == 200:
            st.markdown("### 📋 Summary")
            st.markdown(data["summary"])
        else:
            st.error(f"Summarisation failed: {data.get('detail', 'Unknown error')}")
