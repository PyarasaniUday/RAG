from typing import List
from langchain_core.documents import Document
from src.vectorstore.chroma_store import get_vector_store
from src.utils.helpers import logger, load_config

def retrieve_relevant_documents(query: str) -> List[Document]:
    """Retrieves relevant document chunks from Chroma vector store using similarity search."""
    if not query.strip():
        logger.warning("Empty query received for retrieval.")
        return []
        
    config = load_config()
    retrieval_config = config.get("retrieval", {})
    top_k = retrieval_config.get("top_k", 5)
    
    logger.info(f"Retrieving relevant documents for query: '{query}' (top_k={top_k})")
    
    try:
        vector_store = get_vector_store()
        # similarity_search converts the text query to embeddings internally using the initialized embedding function
        results = vector_store.similarity_search(query, k=top_k)
        logger.info(f"Retrieved {len(results)} relevant chunks.")
        
        # Log basic metadata for retrieval debugging
        for idx, doc in enumerate(results):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "unknown")
            logger.info(f"Chunk {idx+1}: Source={source}, Page={page}")
            
        return results
    except Exception as e:
        logger.error(f"Failed to perform similarity search: {e}", exc_info=True)
        raise e
