from src.alerts.formatter import format_alert_text


def test_format_alert_text():
    alerts = [
        {
            "borough": "BROOKLYN",
            "category": "Noise",
            "start_time": "10:00 PM",
            "end_time": "11:00 PM",
            "current_count": 25,
            "threshold": 18.2,
            "historical_count": 52,
        }
    ]

    result = format_alert_text(alerts)
    assert "BROOKLYN — Noise" in result
    assert "10:00 PM – 11:00 PM" in result
    assert "25 complaints" in result
    assert "Historical threshold: 18.2" in result
    assert "Based on 52 comparable periods" in result


def test_format_alert_text_multiple_conditions():
        alerts = [
        {
            "borough": "BROOKLYN",
            "category": "Noise",
            "start_time": "10:00 PM",
            "end_time": "11:00 PM",
            "current_count": 25,
            "threshold": 18.2,
            "historical_count": 52,
        },
        {
            "borough": "QUEENS",
            "category": "Noise",
            "start_time": "10:00 PM",
            "end_time": "11:00 PM",
            "current_count": 31,
            "threshold": 20.1,
            "historical_count": 52,
        },
    ]

        result = format_alert_text(alerts)

        assert "BROOKLYN — Noise" in result
        assert "QUEENS — Noise" in result