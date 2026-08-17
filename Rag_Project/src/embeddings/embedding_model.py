from src.utils.helpers import logger, load_config

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback to older langchain-community if needed, though langchain-huggingface is standard now
    from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model() -> HuggingFaceEmbeddings:
    """Loads and returns the configured embedding model instance."""
    config = load_config()
    embeddings_config = config.get("embeddings", {})
    model_name = embeddings_config.get("model", "all-MiniLM-L6-v2")
    
    logger.info(f"Initializing embedding model: {model_name}")
    try:
        # HuggingFaceEmbeddings downloads model locally on first run if not present
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Default to CPU for maximum compatibility
            encode_kwargs={'normalize_embeddings': False}
        )
        logger.info("Embedding model initialized successfully.")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}", exc_info=True)
        raise e
