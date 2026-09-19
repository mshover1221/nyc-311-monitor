from datetime import datetime
from unittest.mock import patch

from src.alerts.runner import ALERT_RECIPIENT, run_alert_evaluation


def test_run_alert_evaluation_returns_formatted_alert():
    start_time = datetime(2026, 2, 7, 22, 0)
    end_time = datetime(2026, 2, 7, 23, 0)

    triggered_condition = {
        "borough": "BROOKLYN",
        "category": "Noise",
        "start_time": "10:00 PM",
        "end_time": "11:00 PM",
        "current_count": 25,
        "threshold": 18.2,
        "historical_count": 52,
        "unusual": True,
    }

    with patch("src.alerts.runner.evaluate_conditions"), \
         patch("src.alerts.runner.get_triggered_conditions") as mock_get_triggered, \
         patch("src.alerts.runner.format_alert_text") as mock_format, \
         patch("src.alerts.runner.send_email") as mock_send_email:

        mock_get_triggered.return_value = [triggered_condition]
        mock_format.return_value = "formatted alert"

        result = run_alert_evaluation(start_time, end_time)

    assert result == "formatted alert"
    mock_format.assert_called_once_with([triggered_condition])
    mock_send_email.assert_called_once_with(
        "NYC 311 Alert",
        "formatted alert",
        ALERT_RECIPIENT,
    )


def test_run_alert_evaluation_returns_none_when_no_alerts():
    start_time = datetime(2026, 2, 7, 22, 0)
    end_time = datetime(2026, 2, 7, 23, 0)

    with patch("src.alerts.runner.evaluate_conditions"), \
         patch("src.alerts.runner.get_triggered_conditions") as mock_get_triggered, \
         patch("src.alerts.runner.format_alert_text") as mock_format, \
         patch("src.alerts.runner.send_email") as mock_send_email:

        mock_get_triggered.return_value = []

        result = run_alert_evaluation(start_time, end_time)

    assert result is None
    mock_format.assert_not_called()
    mock_send_email.assert_not_called()


def test_run_alert_evaluation_raises_when_recipient_is_missing():
    start_time = datetime(2026, 2, 7, 22, 0)
    end_time = datetime(2026, 2, 7, 23, 0)

    triggered_condition = {
        "borough": "BROOKLYN",
        "category": "Noise",
        "start_time": "10:00 PM",
        "end_time": "11:00 PM",
        "current_count": 25,
        "threshold": 18.2,
        "historical_count": 52,
        "unusual": True,
    }

    with patch("src.alerts.runner.evaluate_conditions"), \
         patch("src.alerts.runner.get_triggered_conditions") as mock_get_triggered, \
         patch("src.alerts.runner.format_alert_text") as mock_format, \
         patch("src.alerts.runner.send_email") as mock_send_email, \
         patch("src.alerts.runner.ALERT_RECIPIENT", None):

        mock_get_triggered.return_value = [triggered_condition]
        mock_format.return_value = "formatted alert"

        try:
            run_alert_evaluation(start_time, end_time)
            assert False, "Expected RuntimeError"
        except RuntimeError as error:
            assert str(error) == (
                "ALERT_RECIPIENT is not set in environment variables"
            )

    mock_send_email.assert_not_called()



