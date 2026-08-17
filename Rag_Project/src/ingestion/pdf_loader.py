import os
import glob
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from src.utils.helpers import logger, load_config, get_project_path

def get_pdf_files(pdf_dir: str) -> List[str]:
    """Finds all PDF files in the specified directory."""
    search_path = os.path.join(pdf_dir, "*.pdf")
    pdf_files = glob.glob(search_path)
    logger.info(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
    return pdf_files

def load_single_pdf(file_path: str) -> List[Document]:
    """Loads a single PDF file using PyPDFLoader and returns a list of Document objects."""
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found at path: {file_path}")
        raise FileNotFoundError(f"PDF file not found at path: {file_path}")
        
    try:
        logger.info(f"Loading PDF file: {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Enforce metadata checks and set standardized source/page attributes
        for doc in docs:
            # PyPDFLoader usually populates 'source' and 'page' in metadata.
            # Make sure source is just the filename, not the full system path, or store both
            full_path = doc.metadata.get("source", file_path)
            filename = os.path.basename(full_path)
            doc.metadata["filename"] = filename
            doc.metadata["source"] = filename
            if "page" not in doc.metadata:
                doc.metadata["page"] = 0 # Default if page is missing
                
        logger.info(f"Successfully loaded {len(docs)} pages from {file_path}")
        return docs
    except Exception as e:
        logger.error(f"Failed to load PDF file {file_path}: {e}", exc_info=True)
        raise e

def load_all_pdfs() -> List[Document]:
    """Loads all PDF files from the configured PDF directory."""
    config = load_config()
    pdf_rel_dir = config.get("pdf_directory", "data/documents/pdfs")
    pdf_dir = get_project_path(pdf_rel_dir)
    
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        logger.info(f"Created empty PDF directory at: {pdf_dir}")
        return []
        
    pdf_files = get_pdf_files(pdf_dir)
    all_documents = []
    
    for pdf_file in pdf_files:
        try:
            docs = load_single_pdf(pdf_file)
            all_documents.extend(docs)
        except Exception as e:
            logger.warning(f"Skipping failed PDF file {pdf_file}: {e}")
            
    logger.info(f"Loaded a total of {len(all_documents)} document pages from all PDFs")
    return all_documents
