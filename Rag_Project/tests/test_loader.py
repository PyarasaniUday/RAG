import os
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from src.ingestion.pdf_loader import load_single_pdf, load_all_pdfs

@patch("src.ingestion.pdf_loader.PyPDFLoader")
def test_load_single_pdf(mock_pypdf_loader):
    # Setup mock documents returned by loader
    mock_doc1 = Document(page_content="Page 1 content", metadata={"source": "test_path/dummy.pdf", "page": 0})
    mock_doc2 = Document(page_content="Page 2 content", metadata={"source": "test_path/dummy.pdf", "page": 1})
    
    mock_loader_instance = MagicMock()
    mock_loader_instance.load.return_value = [mock_doc1, mock_doc2]
    mock_pypdf_loader.return_value = mock_loader_instance
    
    # Mock os.path.exists to return True for our fake file
    with patch("os.path.exists", return_value=True):
        docs = load_single_pdf("test_path/dummy.pdf")
        
    assert len(docs) == 2
    assert docs[0].page_content == "Page 1 content"
    assert docs[0].metadata["source"] == "dummy.pdf"
    assert docs[0].metadata["filename"] == "dummy.pdf"
    assert docs[0].metadata["page"] == 0
    assert docs[1].metadata["page"] == 1
    
    mock_pypdf_loader.assert_called_once_with("test_path/dummy.pdf")
    mock_loader_instance.load.assert_called_once()

@patch("src.ingestion.pdf_loader.get_pdf_files")
@patch("src.ingestion.pdf_loader.load_single_pdf")
@patch("src.ingestion.pdf_loader.load_config")
def test_load_all_pdfs(mock_load_config, mock_load_single_pdf, mock_get_pdf_files):
    # Mock configuration and files found
    mock_load_config.return_value = {"pdf_directory": "data/documents/pdfs"}
    mock_get_pdf_files.return_value = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
    
    # Mock return values for load_single_pdf
    doc1 = Document(page_content="Doc 1 content", metadata={"source": "doc1.pdf", "page": 0})
    doc2 = Document(page_content="Doc 2 content", metadata={"source": "doc2.pdf", "page": 0})
    
    mock_load_single_pdf.side_effect = [[doc1], [doc2]]
    
    with patch("os.path.exists", return_value=True):
        all_docs = load_all_pdfs()
        
    assert len(all_docs) == 2
    assert all_docs[0].metadata["source"] == "doc1.pdf"
    assert all_docs[1].metadata["source"] == "doc2.pdf"
    
    assert mock_load_single_pdf.call_count == 2
