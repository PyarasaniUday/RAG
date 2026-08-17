from typing import List
from langchain_core.documents import Document

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # pyrefly: ignore [missing-import]
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils.helpers import logger, load_config

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Splits a list of Documents into smaller chunks based on config.yaml parameters."""
    if not documents:
        logger.warning("No documents provided for chunking.")
        return []
        
    config = load_config()
    chunking_config = config.get("chunking", {})
    chunk_size = chunking_config.get("chunk_size", 1000)
    chunk_overlap = chunking_config.get("chunk_overlap", 200)
    
    logger.info(f"Chunking {len(documents)} documents (chunk_size={chunk_size}, chunk_overlap={chunk_overlap}).")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True  # Helpful metadata for locating where the chunk starts
    )
    
    try:
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split completed. Created {len(chunks)} chunks.")
        
        # Verify metadata is preserved
        for chunk in chunks:
            if "source" not in chunk.metadata:
                logger.warning(f"Chunk missing 'source' metadata: {chunk.metadata}")
                
        return chunks
    except Exception as e:
        logger.error(f"Failed to chunk documents: {e}", exc_info=True)
        raise e
