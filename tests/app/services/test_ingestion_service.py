import pytest
from unittest.mock import patch
from src.services import ingestion_service

@patch("app.services.ingestion_service.some_external_api")
def test_ingest_item_success(mock_api):
    mock_api.return_value = {"result": "ok"}
    result = ingestion_service.ingest_item("item_id")
    assert result["result"] == "ok"
    mock_api.assert_called_once_with("item_id")

@patch("app.services.ingestion_service.some_external_api")
def test_ingest_item_failure(mock_api):
    mock_api.side_effect = Exception("fail")
    with pytest.raises(Exception):
        ingestion_service.ingest_item("item_id")
