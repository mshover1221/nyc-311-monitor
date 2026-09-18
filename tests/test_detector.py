from unittest.mock import patch
from src.alerts.detector import calculate_threshold
from src.alerts.detector import evaluate_conditions
from src.alerts.detector import get_triggered_conditions

def test_calculate_threshold():
    counts = [10, 12, 14, 16, 18]
    threshold = calculate_threshold(counts)
    assert threshold == 17.6


def test_evaluate_conditions():
    conditions = [
        ("BROOKLYN", "Noise"),
        ("QUEENS", "Noise"),
    ]

    with patch("src.alerts.detector.is_unusual") as mock_is_unusual:
        mock_is_unusual.side_effect = [
            {
                "current_count": 10,
                "threshold": 15.0,
                "historical_count": 52,
                "unusual": False
            },
            {
                "current_count": 25,
                "threshold": 18.0,
                "historical_count": 52,
                "unusual": True
            }
        ]

        results = evaluate_conditions(
            None,
            None,
            None,
            conditions
        )

        assert results == [
            {
                "borough": "BROOKLYN",
                "category": "Noise",
                "start_time": None,
                "end_time": None,
                "current_count": 10,
                "threshold": 15.0,
                "historical_count": 52,
                "unusual": False
            },
            {
                "borough": "QUEENS",
                "category": "Noise",
                "start_time": None,
                "end_time": None,
                "current_count": 25,
                "threshold": 18.0,
                "historical_count": 52,
                "unusual": True
            }
        ]


def test_get_triggered_conditions():
    results = [
        {"borough": "BROOKLYN", "category": "Noise", "unusual": False},
        {"borough": "BROOKLYN", "category": "Water System", "unusual": True},
        {"borough": "QUEENS", "category": "Noise", "unusual": True},
    ]

    triggered = get_triggered_conditions(results)

    assert triggered == [
        {"borough": "BROOKLYN", "category": "Water System", "unusual": True},
        {"borough": "QUEENS", "category": "Noise", "unusual": True},
    ]

