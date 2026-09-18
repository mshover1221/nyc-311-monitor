from src.email.email_sender import send_email

from unittest.mock import patch


def test_send_email_success():
    fake_response = type("Response", (), {"status_code": 202})()

    with patch("src.email.email_sender.SendGridAPIClient") as mock_client:
        mock_client.return_value.send.return_value = fake_response

        result = send_email(
            "Test Alert",
            "This is a test alert.",
            "test@example.com",
        )

        assert result is True


def test_send_email_failure():
    fake_response = type("Response", (), {"status_code": 400, "body": b"Bad request"})()
    with patch("src.email.email_sender.SendGridAPIClient") as mock_client:
        mock_client.return_value.send.return_value = fake_response

        result = send_email(
            "Test Alert",
            "This is a test alert.",
            "test@example.com",
        )

        assert result is False


def test_send_email_exception():
    with patch("src.email.email_sender.SendGridAPIClient") as mock_client:
        mock_client.return_value.send.side_effect = Exception("Network error")

        result = send_email(
            "Test Alert",
            "This is a test alert.",
            "test@example.com",
        )

        assert result is False