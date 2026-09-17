from unittest.mock import patch
from src.alerts.detector import calculate_threshold
from src.alerts.detector import evaluate_conditions

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

        mock_is_unusual.side_effect = [False, True]

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
                "unusual": False
            },
            {
                "borough": "QUEENS",
                "category": "Noise",
                "unusual": True
            }
        ]