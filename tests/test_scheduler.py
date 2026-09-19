from datetime import datetime
from unittest.mock import patch

from src.app.scheduler import alert_job


def test_alert_job_evaluates_previous_completed_hour():
    now = datetime(2026, 2, 7, 23, 37)

    with patch("src.app.scheduler.run_alerts_only") as mock_run_alerts:
        alert_job(now)

    mock_run_alerts.assert_called_once_with(
        datetime(2026, 2, 7, 22, 0),
        datetime(2026, 2, 7, 23, 0),
    )

