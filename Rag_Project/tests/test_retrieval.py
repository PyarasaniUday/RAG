from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from src.retrieval.similarity_search import retrieve_relevant_documents

@patch("src.retrieval.similarity_search.get_vector_store")
@patch("src.retrieval.similarity_search.load_config")
def test_retrieve_relevant_documents(mock_load_config, mock_get_vector_store):
    mock_load_config.return_value = {
        "retrieval": {
            "top_k": 3
        }
    }
    
    mock_docs = [
        Document(page_content="Content 1", metadata={"source": "doc1.pdf", "page": 1}),
        Document(page_content="Content 2", metadata={"source": "doc2.pdf", "page": 2})
    ]
    
    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = mock_docs
    mock_get_vector_store.return_value = mock_vector_store
    
    results = retrieve_relevant_documents("test query")
    
    assert len(results) == 2
    assert results[0].page_content == "Content 1"
    assert results[0].metadata["source"] == "doc1.pdf"
    
    mock_vector_store.similarity_search.assert_called_once_with("test query", k=3)
