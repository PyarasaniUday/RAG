import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from src.retrieval.similarity_search import retrieve_relevant_documents
from src.context.page_extractor import extract_sources_and_context
from src.prompts.prompt_template import format_rag_prompt
from src.llm.llm_client import generate_answer
from src.utils.helpers import logger, load_config, get_project_path

router = APIRouter()

# Input Validation Models
class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language question to ask the document assistant.")

class SourceInfo(BaseModel):
    file: str = Field(..., description="The source document name.")
    page: int = Field(..., description="The page number where the information was retrieved.")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="The generated technical response.")
    sources: List[SourceInfo] = Field(..., description="The source citations for the answer.")

class DocumentListResponse(BaseModel):
    documents: List[str] = Field(..., description="List of PDF files available in the ingestion directory.")

# ROOT PAGE
@router.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serves the index.html frontend interface."""
    index_path = get_project_path("src/api/static/index.html")
    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend files not found."
        )
    return FileResponse(index_path)

# GET DOCUMENTS
@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """Lists all PDF documents in the ingestion folder."""
    config = load_config()
    pdf_rel_dir = config.get("pdf_directory", "data/documents/pdfs")
    pdf_dir = get_project_path(pdf_rel_dir)
    
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        
    try:
        files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
        return DocumentListResponse(documents=files)
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not access PDF files list."
        )

# UPLOAD DOCUMENT
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF document to the ingestion directory."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported."
        )
        
    config = load_config()
    pdf_rel_dir = config.get("pdf_directory", "data/documents/pdfs")
    pdf_dir = get_project_path(pdf_rel_dir)
    
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        
    file_path = os.path.join(pdf_dir, os.path.basename(file.filename))
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File uploaded successfully: {file.filename}")
        return {"filename": file.filename, "message": "File uploaded successfully."}
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

# DELETE DOCUMENT
@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Deletes a PDF document from the ingestion directory."""
    config = load_config()
    pdf_rel_dir = config.get("pdf_directory", "data/documents/pdfs")
    pdf_dir = get_project_path(pdf_rel_dir)
    
    file_path = os.path.join(pdf_dir, os.path.basename(filename))
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{filename}' not found."
        )
        
    try:
        os.remove(file_path)
        logger.info(f"File deleted successfully: {filename}")
        return {"filename": filename, "message": "File deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

# TRIGGER INGESTION
@router.post("/ingest")
async def trigger_ingestion():
    """Triggers the document loading, chunking, and database rebuilding pipeline."""
    try:
        logger.info("API triggered ingestion execution.")
        from src.ingestion.pdf_loader import load_all_pdfs
        from src.chunking.text_chunker import chunk_documents
        from src.vectorstore.chroma_store import rebuild_vector_store
        
        # 1. Load PDFs
        docs = load_all_pdfs()
        if not docs:
            logger.info("Ingestion skipped: No PDFs found.")
            return {"status": "skipped", "message": "No PDFs found in the input folder to ingest."}
            
        # 2. Split
        chunks = chunk_documents(docs)
        
        # 3. Embed & persist in vector store
        rebuild_vector_store(chunks)
        
        logger.info("API triggered ingestion completed successfully.")
        return {"status": "success", "message": f"Successfully reindexed {len(chunks)} chunks from {len(docs)} pages."}
    except Exception as e:
        logger.error(f"API Ingestion trigger failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )

# QUERY ENDPOINT
@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Processes user query through the similarity search, context formatting, and LLM answer generation pipeline."""
    query_text = request.query.strip()
    if not query_text:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Query cannot be empty."
         )
         
    logger.info(f"API received query: '{query_text}'")
    
    try:
        # 1. Similarity Search
        retrieved_docs = retrieve_relevant_documents(query_text)
        
        # 2. Handle empty results case
        if not retrieved_docs:
            logger.info("No relevant documents found. Returning early safe response.")
            return QueryResponse(
                answer="I could not find this information in the provided documents.",
                sources=[]
            )
            
        # 3. Context & Metadata Extraction
        context_str, sources = extract_sources_and_context(retrieved_docs)
        
        # 4. Prompt construction
        prompt = format_rag_prompt(context=context_str, question=query_text)
        
        # 5. LLM Answer generation
        answer = generate_answer(prompt)
        
        return QueryResponse(
            answer=answer,
            sources=[SourceInfo(**s) for s in sources]
        )
        
    except Exception as e:
        logger.error(f"Error processing query endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {str(e)}"
        )

# HEALTH ENDPOINT
@router.get("/health")
async def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy"}
