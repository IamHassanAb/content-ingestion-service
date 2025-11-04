import pytest
from unittest.mock import patch
from src.services import pipeline


@patch("app.services.pipeline.some_dependency")
def test_run_pipeline_success(mock_dep):
    mock_dep.return_value = "ok"
    result = pipeline.run_pipeline("input_data")
    assert result == "ok"
    mock_dep.assert_called_once_with("input_data")


@patch("app.services.pipeline.some_dependency")
def test_run_pipeline_failure(mock_dep):
    mock_dep.side_effect = Exception("fail")
    with pytest.raises(Exception):
        pipeline.run_pipeline("input_data")
