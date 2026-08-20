# Tech Fusion — PDF-based Retrieval-Augmented Generation (RAG) Repository

Welcome to the **Tech Fusion** Git repository. This repository contains a modular, production-style Retrieval-Augmented Generation (RAG) system designed to load, chunk, embed, and index technical PDF documents into a local vector store, and perform context-grounded querying via the Google Gemini API.

---

## 📁 Repository Structure

The repository is structured as followss:

* **[README.md](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/README.md)** (this file): Root-level repository guide and overview.
* **[Rag_Project/](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/)**: The core RAG application workspace containing:
  * **[Rag_Project/README.md](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/README.md)**: Detailed step-by-step setup, configuration, and API reference.
  * **[Rag_Project/main.py](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/main.py)**: Main entry point for document ingestion and running the FastAPI server.
  * **[Rag_Project/requirements.txt](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/requirements.txt)**: Python package dependencies.
  * **[Rag_Project/config.yaml](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/config.yaml)**: YAML configuration for embeddings, vector store parameters, and LLM model prompts.
  * **[Rag_Project/src/](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/src/)**: Source modules for PDF ingestion, chunking, embeddings, vector database persistence, context retrieval, prompts, LLM client, and FastAPI routes.
  * **[Rag_Project/tests/](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/tests/)**: Automated unit/integration tests with mocks.

---

## 🛠️ Tech Stack & Key Technologies

* **Backend API**: Python, FastAPI, Uvicorn, Pydantic
* **RAG Orchestrator**: LangChain & LangChain Community
* **Document Parser**: PyPDF
* **Vector Database**: ChromaDB (local persistent storage)
* **Local Embeddings Model**: HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)
* **Large Language Model**: Google Gemini (`gemini-1.5-flash` via `langchain-google-genai`)
* **Testing Suite**: PyTest

---

## ⚙️ How It Works (Pipeline)

```text
PDF Documents → PyPDF Extraction → Text Chunking (Recursive Splitter) → Embeddings Generation (Sentence Transformers) → Chroma Vector DB (Persistence)
                                                                                                                           ↓
Query Answer ← Google Gemini LLM Response ← Context Grounded Prompt Builder ← Semantic Similarity Retrieval Search ← User Query Input
```

1. **Ingestion**: Raw PDFs placed in `data/documents/pdfs/` are loaded using PyPDF.
2. **Chunking & Embedding**: The text is chunked using a `RecursiveCharacterTextSplitter` and converted into vector embeddings.
3. **Storage**: Embeddings are stored in a persistent local Chroma database.
4. **Retrieval**: When a query is run, the vector database finds the top-K matching chunks.
5. **Generation**: The matches are compiled into a prompt and sent to Google Gemini, which generates a grounded response citing page and file sources.

---

## 🚀 Quick Start Guide

To run the application locally, follow these steps:

### 1. Set Up Environment
Navigate into the project folder, create a virtual environment, and install dependencies:
```powershell
cd Rag_Project
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Credentials
Create a `.env` file in the `Rag_Project` directory based on `.env.example`:
```text
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Place Documents & Ingest
Place your PDF files in `Rag_Project/data/documents/pdfs/` and run the ingestion pipeline:
```powershell
python main.py --ingest
```

### 4. Run the API Server
Start the FastAPI server:
```powershell
uvicorn main:app --reload
```
You can access the API interactive documentation at `http://127.0.0.1:8000/docs` and send POST requests to the `/query` endpoint.

For more granular details, refer to the project's internal **[Rag_Project/README.md](file:///c:/Users/UDAY%20KUMAR/OneDrive/Desktop/EL_KMCE/RAG_EXERCISES/RAG/Rag_Project/README.md)**.
