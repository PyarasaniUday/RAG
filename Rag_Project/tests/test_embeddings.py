from unittest.mock import MagicMock, patch
from src.embeddings.embedding_model import get_embedding_model

@patch("src.embeddings.embedding_model.HuggingFaceEmbeddings")
@patch("src.embeddings.embedding_model.load_config")
def test_get_embedding_model(mock_load_config, mock_huggingface_embeddings):
    mock_load_config.return_value = {
        "embeddings": {
            "model": "all-MiniLM-L6-v2"
        }
    }
    
    mock_instance = MagicMock()
    mock_huggingface_embeddings.return_value = mock_instance
    
    embeddings = get_embedding_model()
    
    assert embeddings == mock_instance
    mock_huggingface_embeddings.assert_called_once_with(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
