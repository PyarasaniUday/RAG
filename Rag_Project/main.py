import sys
import argparse
import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as api_router
from src.utils.helpers import logger, get_project_path

# Initialize FastAPI application
app = FastAPI(
    title="Tech Fusion RAG API",
    description="A modular RAG application for querying technical PDFs.",
    version="1.0.0"
)

# Register routes
app.include_router(api_router)

# Mount static files for the web UI
static_dir = get_project_path("src/api/static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files from {static_dir}")
else:
    logger.warning(f"Static directory not found at {static_dir}. Frontend will not be served.")

def run_ingestion():
    """Independent ingestion pipeline execution to load, chunk, embed, and store PDFs."""
    logger.info("Initializing offline ingestion pipeline.")
    print("=== Tech Fusion Ingestion Pipeline ===")
    
    # 1. PDF Loading
    from src.ingestion.pdf_loader import load_all_pdfs
    print("[1/4] Loading PDF documents...")
    docs = load_all_pdfs()
    if not docs:
        print("[-] No PDF documents found. Please check data/documents/pdfs/ directory.")
        logger.warning("Ingestion stopped: No PDF documents found.")
        return
    print(f"[+] Loaded {len(docs)} pages.")
    
    # 2. Chunking
    from src.chunking.text_chunker import chunk_documents
    print("[2/4] Splitting documents into chunks...")
    chunks = chunk_documents(docs)
    print(f"[+] Split into {len(chunks)} chunks.")
    
    # 3. Embedding & Vector Store (Chroma)
    from src.vectorstore.chroma_store import rebuild_vector_store
    print("[3/4] Generating embeddings and rebuilding Chroma database...")
    rebuild_vector_store(chunks)
    print("[4/4] Ingestion pipeline run completed successfully.")
    logger.info("Ingestion completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tech Fusion RAG Application Interface")
    parser.add_argument(
        "--ingest", 
        action="store_true", 
        help="Run the document ingestion pipeline to load PDFs and populate the vector store."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host interface to run the FastAPI server on (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the FastAPI server on (default: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.ingest:
        run_ingestion()
    else:
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
