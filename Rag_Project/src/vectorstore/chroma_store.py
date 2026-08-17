import os
import shutil
from typing import List
from langchain_core.documents import Document
from src.embeddings.embedding_model import get_embedding_model
from src.utils.helpers import logger, load_config, get_project_path

try:
    # pyrefly: ignore [missing-import]
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

def get_vector_store() -> Chroma:
    """Loads and returns the persisted Chroma vector store instance."""
    config = load_config()
    chroma_rel_dir = config.get("chroma_directory", "data/chroma_db")
    chroma_dir = get_project_path(chroma_rel_dir)
    collection_name = config.get("collection_name", "tech_fusion_documents")
    
    # Initialize embedding model to be passed into Chroma
    embeddings = get_embedding_model()
    
    logger.info(f"Loading Chroma vector store at {chroma_dir} (collection: {collection_name})")
    
    try:
        # langchain_chroma / chromadb will automatically create path if it doesn't exist
        vector_store = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        return vector_store
    except Exception as e:
        logger.error(f"Failed to load Chroma vector store: {e}", exc_info=True)
        raise e

def add_documents_to_store(documents: List[Document]) -> Chroma:
    """Adds a list of Document chunks to the vector store and persists them."""
    if not documents:
        logger.warning("No documents provided to add to Chroma.")
        return get_vector_store()
        
    logger.info(f"Adding {len(documents)} chunks to Chroma vector store.")
    vector_store = get_vector_store()
    
    try:
        vector_store.add_documents(documents)
        logger.info("Successfully added documents and persisted store.")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to add documents to Chroma: {e}", exc_info=True)
        raise e

def rebuild_vector_store(documents: List[Document]) -> Chroma:
    """Deletes existing vector store directory and creates a new one with the given documents."""
    config = load_config()
    chroma_rel_dir = config.get("chroma_directory", "data/chroma_db")
    chroma_dir = get_project_path(chroma_rel_dir)
    
    logger.info(f"Rebuilding vector store. Clearing database path: {chroma_dir}")
    try:
        # Remove database directory if exists to ensure clean rebuild
        if os.path.exists(chroma_dir):
            # Close/clean references if necessary. 
            # On Windows, sometimes directories are locked if Chroma is still active.
            # Using shutil.rmtree might fail if files are open. Let's try to remove it.
            try:
                shutil.rmtree(chroma_dir)
                logger.info("Deleted existing Chroma directory successfully.")
            except Exception as rmtree_err:
                logger.warning(f"Could not delete Chroma directory {chroma_dir} via rmtree: {rmtree_err}. Proceeding to add documents directly.")
                
        # Recreate directory structure
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Build vector store from scratch
        return add_documents_to_store(documents)
    except Exception as e:
        logger.error(f"Failed to rebuild vector store: {e}", exc_info=True)
        raise e
