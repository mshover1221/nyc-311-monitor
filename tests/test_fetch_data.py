"""Tests for NYC 311 data fetching and retry behavior."""

from datetime import datetime
from unittest.mock import Mock, patch

from src.app.fetch_data import fetch_311_data


def test_retries_after_503():
    with patch("src.app.fetch_data.requests.get") as mock_get:
        response_503 = Mock()
        response_503.status_code = 503

        response_200 = Mock()
        response_200.status_code = 200
        response_200.json.return_value = [
            {"created_date": "2026-09-04T23:59:00.000"}
        ]


        mock_get.side_effect = [response_503, response_200]

        fetch_311_data(
            datetime(2026, 9, 4),
            datetime(2026, 9, 5),
            10
        )

        assert mock_get.call_count == 2

