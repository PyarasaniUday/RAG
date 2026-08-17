from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_query_endpoint_empty_query():
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

@patch("src.api.routes.retrieve_relevant_documents")
def test_query_endpoint_no_context(mock_retrieve):
    # Mock retrieve returning empty list (no documents matched query)
    mock_retrieve.return_value = []
    
    response = client.post("/query", json={"query": "unrelated topic"})
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["answer"] == "I could not find this information in the provided documents."
    assert res_data["sources"] == []
    mock_retrieve.assert_called_once_with("unrelated topic")

@patch("src.api.routes.generate_answer")
@patch("src.api.routes.extract_sources_and_context")
@patch("src.api.routes.retrieve_relevant_documents")
def test_query_endpoint_success(mock_retrieve, mock_extract, mock_generate):
    from langchain_core.documents import Document
    # Setup mocks
    mock_docs = [Document(page_content="some text", metadata={"source": "test.pdf", "page": 0})]
    mock_retrieve.return_value = mock_docs
    
    mock_extract.return_value = ("formatted context", [{"file": "test.pdf", "page": 1}])
    mock_generate.return_value = "generated llm answer"
    
    response = client.post("/query", json={"query": "what is x?"})
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["answer"] == "generated llm answer"
    assert len(res_data["sources"]) == 1
    assert res_data["sources"][0]["file"] == "test.pdf"
    assert res_data["sources"][0]["page"] == 1
    
    mock_retrieve.assert_called_once_with("what is x?")
    mock_extract.assert_called_once_with(mock_docs)
    mock_generate.assert_called_once()
