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


def test_get_historical_counts_filters_by_weekday_and_season():
    class FakeRow:
        def __init__(self, date, count):
            self.date = date
            self.count = count

    fake_rows = [
        FakeRow("2026-07-04", 2),   # Saturday, Summer -> include
        FakeRow("2026-07-18", 3),   # Saturday, Summer -> include
        FakeRow("2026-07-24", 9),   # Friday, Summer -> exclude
        FakeRow("2026-06-27", 4),   # Saturday, Summer -> include
        FakeRow("2026-03-28", 8),   # Saturday, Spring -> exclude
    ]

    class FakeQuery:
        def filter(self, *args):
            return self

        def group_by(self, *args):
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
    assert result.count(0) == 10
    assert 2 in result
    assert 3 in result
    assert 4 in result
    assert 9 not in result
    assert 8 not in result


def test_is_unusual_skips_sparse_history():
    from src.alerts.detector import is_unusual

    historical_counts = [0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    with patch(
        "src.alerts.detector.get_current_count",
        return_value=10,
    ), patch(
        "src.alerts.detector.get_historical_counts",
        return_value=historical_counts,
    ):
        result = is_unusual(
            None,
            "BROOKLYN",
            "Rodents",
            datetime(2026, 7, 25, 22),
            datetime(2026, 7, 25, 23),
        )

    assert result["current_count"] == 10
    assert result["historical_count"] == 13
    assert result["nonzero_historical_count"] == 1
    assert result["threshold"] is None
    assert result["unusual"] is False


def test_is_unusual_allows_three_nonzero_periods():
    from src.alerts.detector import is_unusual

    historical_counts = [0, 0, 5, 0, 8, 0, 0, 12, 0, 0, 0, 0, 0]

    with patch(
        "src.alerts.detector.get_current_count",
        return_value=20,
    ), patch(
        "src.alerts.detector.get_historical_counts",
        return_value=historical_counts,
    ):
        result = is_unusual(
            None,
            "BROOKLYN",
            "Rodents",
            datetime(2026, 7, 25, 22),
            datetime(2026, 7, 25, 23),
        )

    assert result["nonzero_historical_count"] == 3
    assert result["threshold"] is not None
    assert result["unusual"] is True


def test_is_unusual_does_not_alert_at_threshold():
    from src.alerts.detector import is_unusual, calculate_threshold

    historical_counts = [0, 0, 5, 0, 8, 0, 0, 12, 0, 0, 0, 0, 0]
    threshold = calculate_threshold(historical_counts)

    with patch(
        "src.alerts.detector.get_current_count",
        return_value=threshold,
    ), patch(
        "src.alerts.detector.get_historical_counts",
        return_value=historical_counts,
    ):
        result = is_unusual(
            None,
            "BROOKLYN",
            "Rodents",
            datetime(2026, 7, 25, 22),
            datetime(2026, 7, 25, 23),
        )

    assert result["threshold"] == threshold
    assert result["current_count"] == threshold
    assert result["unusual"] is False
