# Tech Fusion — Complete RAG Project

Tech Fusion is a production-style, modular PDF-based Retrieval-Augmented Generation (RAG) application. It allows users to query technical PDF documents and receive accurate, source-cited responses from an LLM backed by a local Chroma vector database.

## Problem Statement
Technical documents (such as APIs, system architectures, textbook notes, and documentation) are often large, dense, and difficult to search through efficiently. General-purpose LLMs lack knowledge of specific private or custom technical documents and tend to hallucinate when asked about specific details they weren't trained on.

## Solution
Tech Fusion solves this problem by using a Retrieval-Augmented Generation (RAG) pipeline. When a user asks a question, the system retrieves only the most relevant sections of the uploaded PDF files from a persistent vector database, constructs a structured prompt containing the retrieved context, and queries the LLM. The LLM then generates an answer grounded strictly in the provided documents, citing the file source and page numbers.

---

## Architectural Pipeline
The project follows this exact linear flow:

```text
PDF
 ↓
PyPDFLoader (langchain_community)
 ↓
Documents (page_content + metadata)
 ↓
Chunking (RecursiveCharacterTextSplitter)
 ↓
Chunks
 ↓
Embeddings (Sentence Transformers - all-MiniLM-L6-v2)
 ↓
Chroma (Persistent Vector Database)
 ↓
Query (User Request)
 ↓
Similarity Search (Retrieve top K chunks)
 ↓
Results (Structured matching documents)
 ↓
Extract Page Content (Compile content, file and page numbers)
 ↓
Context (LLM grounded context block)
 ↓
Prompt (Context + Instruction Template)
 ↓
LLM (Google Gemini - gemini-1.5-flash)
 ↓
Answer (Ground response with Source citations)
```

---

## Project Structure
The repository contains the following files and modules:

```text
tech_fusion_rag/
│
├── README.md               # Project documentation
├── requirements.txt        # Third-party dependencies
├── .env                    # Local environment keys (ignored by Git)
├── .env.example            # Environment variables template
├── .gitignore              # Files to ignore in Git
├── config.yaml             # Application and model configurations
│
├── data/
│   ├── documents/
│   │   ├── pdfs/           # Input PDF folder (place documents here)
│   │   └── processed/      # Optional folder for processed documents
│   └── chroma_db/          # Persistent ChromaDB database folder
│
├── src/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── pdf_loader.py   # PDF scanner and loader using PyPDFLoader
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   └── text_chunker.py # Splitter using RecursiveCharacterTextSplitter
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_model.py # Configures and loads local embeddings
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── chroma_store.py # Persistence and management of ChromaDB
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── similarity_search.py # Retrieval query helper
│   │
│   ├── context/
│   │   ├── __init__.py
│   │   └── page_extractor.py # Context formatter & citation builder
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── prompt_template.py # LLM Prompt system configuration
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_client.py   # Configures and calls Google Gemini API
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # FastAPI routes (/query, /health)
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Config YAML loader & logging initialization
│
├── tests/                  # Step-by-step test files
│   ├── test_loader.py
│   ├── test_chunking.py
│   ├── test_embeddings.py
│   ├── test_retrieval.py
│   └── test_api.py
│
├── logs/
│   └── app.log             # Application logs
│
└── main.py                 # Runner for Ingestion and Server API
```

---

## Technologies Used
* **Backend Framework**: Python, FastAPI, Uvicorn, Pydantic
* **RAG Orchestrator**: LangChain & LangChain Community
* **Loader**: PyPDF
* **Vector Store**: ChromaDB
* **Local Embeddings**: HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)
* **Large Language Model**: Google Gemini (`gemini-1.5-flash` via `langchain-google-genai`)
* **Testing**: PyTest

---

## Installation & Setup

### 1. Clone the repository and navigate to the project directory:
```powershell
cd tech_fusion_rag
```

### 2. Create and activate a Python virtual environment:
```powershell
python -m venv .venv
# On Windows Powershell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install required packages:
```powershell
pip install -r requirements.txt
```

### 4. Setup Environment Variables:
Copy `.env.example` to `.env` and fill in your Google Gemini API key:
```powershell
cp .env.example .env
```
Inside `.env`:
```text
GEMINI_API_KEY=AIzaSy...
```

---

## Adding PDFs and Ingestion

1. Place your target technical PDFs inside the input folder: `data/documents/pdfs/`
2. Run the ingestion pipeline script to load, chunk, embed, and index the PDFs:
   ```powershell
   python main.py --ingest
   ```
This will process the PDFs, generate embeddings, and build the persistent database files in `data/chroma_db/`. You do not need to repeat this step unless your PDFs change.

---

## Running the API

Start the FastAPI application development server:
```powershell
uvicorn main:app --reload
```
The server will boot and run on `http://127.0.0.1:8000`.

### API Endpoints

#### 1. GET `/health`
Returns the status of the server.
* **Example Response**:
  ```json
  {"status": "healthy"}
  ```

#### 2. POST `/query`
Processes user question using context-grounded retrieval.
* **Example Request**:
  ```json
  {
    "query": "What is a Transformer model?"
  }
  ```
* **Example Response**:
  ```json
  {
    "answer": "A Transformer is a deep learning architecture that relies on self-attention mechanisms to compute representations of its input and output without using sequence-aligned RNNs or convolution.",
    "sources": [
      {
        "file": "transformers.pdf",
        "page": 2
      },
      {
        "file": "transformers.pdf",
        "page": 3
      }
    ]
  }
  ```

---

## Testing

Execute the test suite using pytest to verify each pipeline stage in isolation:
```powershell
pytest -v
```
All external network/LLM calls are mocked in tests to allow fast, local validation.

---

## Future Improvements
* Add support for Docx and Markdown file ingestion.
* Implement a user interface (Streamlit, React, or Vue) for a complete visual experience.
* Incorporate Hybrid Search (BM25 + Semantic similarity).
* Add a chat memory/history layer for conversational retrieval.
