import os
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from src.utils.helpers import logger

def extract_sources_and_context(documents: List[Document]) -> Tuple[str, List[Dict[str, Any]]]:
    """Processes retrieved documents.
    
    Returns:
        A tuple of:
          - Formatted context string for the LLM prompt.
          - List of dictionaries containing source filenames and page numbers.
    """
    if not documents:
        logger.info("No documents provided to extract context.")
        return "", []
        
    context_parts = []
    sources = []
    seen_sources = set()
    
    for doc in documents:
        # Extract page_content
        content = doc.page_content.strip()
        
        # Read source metadata
        full_source = doc.metadata.get("source", "unknown")
        # Ensure it's just the file name
        source_file = os.path.basename(full_source)
        
        # Page numbers are 0-indexed in PyPDFLoader, so we display page + 1 (human readable page number)
        # unless it is already formatted. Let's look at what is standard: PyPDFLoader represents pages 0-indexed.
        # Let's keep the raw page number or use 1-based. To be safe, let's store page+1 for display and document
        # that pages are human-indexed (1-based), but let's read doc.metadata.get("page", 0).
        raw_page = doc.metadata.get("page", 0)
        display_page = raw_page + 1 if isinstance(raw_page, int) else raw_page
        
        # Build formatted block for LLM prompt
        context_parts.append(
            f"[Source: {source_file} | Page: {display_page}]\n{content}"
        )
        
        # Add to unique sources list for the final API response
        source_key = (source_file, raw_page)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "file": source_file,
                "page": display_page
            })
            
    formatted_context = "\n\n".join(context_parts)
    logger.info(f"Generated context of size {len(formatted_context)} characters with {len(sources)} sources.")
    return formatted_context, sources
