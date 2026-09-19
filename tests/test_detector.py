from datetime import datetime
from unittest.mock import patch

from src.alerts.detector import calculate_threshold
from src.alerts.detector import evaluate_conditions
from src.alerts.detector import get_historical_counts
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


def test_get_historical_counts_includes_zero_periods():
    class FakeRow:
        def __init__(self, created_date):
            self.created_date = created_date

    fake_rows = [
        FakeRow(datetime(2026, 7, 4, 22, 15)),
        FakeRow(datetime(2026, 7, 4, 22, 30)),
        FakeRow(datetime(2026, 7, 18, 22, 5)),
        FakeRow(datetime(2026, 7, 18, 22, 40)),
        FakeRow(datetime(2026, 7, 18, 22, 55)),
    ]

    class FakeQuery:
        def filter(self, *args):
            return self

        def all(self):
            return fake_rows

    class FakeSession:
        def query(self, *args):
            return FakeQuery()

    result = get_historical_counts(
        FakeSession(),
        "BROOKLYN",
        "Water System",
        datetime(2026, 7, 25, 22),
    )

    assert len(result) == 13
    assert result.count(0) == 11
    assert 2 in result
    assert 3 in result

