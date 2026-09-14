from src.alerts.detector import calculate_threshold

def test_calculate_threshold():
    counts = [10, 12, 14, 16, 18]
    threshold = calculate_threshold(counts)
    assert threshold == 17.6