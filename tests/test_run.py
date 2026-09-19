from unittest.mock import patch

import pytest
import run


def test_run_ingestion_retries_after_failure():
    with (
        patch("run.fetch_311_data") as mock_fetch,
        patch("run.process_dataframe") as mock_process,
        patch("run.save_complaints") as mock_save,
    ):
        mock_fetch.side_effect = [Exception("temporary failure"), "data"]
        mock_process.return_value = "processed"
        mock_save.return_value = 1
        run.run_ingestion()

        assert mock_fetch.call_count == 2

        first_call = mock_fetch.call_args_list[0]
        second_call = mock_fetch.call_args_list[1]

        assert first_call == second_call
        assert mock_process.call_count == 1
        assert mock_save.call_count == 1


def test_run_ingestion_raises_after_retry():
    with patch("run.fetch_311_data") as mock_fetch:
        mock_fetch.side_effect = Exception("temporary failure")

        with pytest.raises(Exception, match="temporary failure"):
            run.run_ingestion()

        assert mock_fetch.call_count == 2
