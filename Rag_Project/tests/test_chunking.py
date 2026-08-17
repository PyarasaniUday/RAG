from unittest.mock import patch
from langchain_core.documents import Document
from src.chunking.text_chunker import chunk_documents

def test_chunk_documents_empty():
    chunks = chunk_documents([])
    assert chunks == []

@patch("src.chunking.text_chunker.load_config")
def test_chunk_documents_splitting(mock_load_config):
    # Mock chunk size to be small so we get multiple chunks
    mock_load_config.return_value = {
        "chunking": {
            "chunk_size": 20,
            "chunk_overlap": 5
        }
    }
    
    doc = Document(
        page_content="This is a very long string that should be split into multiple chunks.",
        metadata={"source": "test_doc.pdf", "page": 0}
    )
    
    chunks = chunk_documents([doc])
    
    # We should get more than 1 chunk since chunk_size is 20
    assert len(chunks) > 1
    
    # Ensure source metadata is preserved
    for chunk in chunks:
        assert chunk.metadata["source"] == "test_doc.pdf"
        assert chunk.metadata["page"] == 0
        assert "start_index" in chunk.metadata
