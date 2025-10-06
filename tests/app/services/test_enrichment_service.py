import pytest
from unittest.mock import patch
from src.services import enrichment_service

@patch("app.services.enrichment_service.some_llm_function")
def test_enrich_item_success(mock_llm):
    mock_llm.return_value = "enriched"
    result = enrichment_service.enrich_item("item_id")
    assert result == "enriched"
    mock_llm.assert_called_once_with("item_id")

@patch("app.services.enrichment_service.some_llm_function")
def test_enrich_item_error(mock_llm):
    mock_llm.side_effect = Exception("error")
    with pytest.raises(Exception):
        enrichment_service.enrich_item("item_id")
