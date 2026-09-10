"""Create daily datetime windows for historical NYC 311 backfills."""

from datetime import datetime, timedelta

def get_backfill_range(days):
    now = datetime.now()

    end = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    start = end - timedelta(days=days)

    return start, end


def get_daily_windows(start, end):
    current = start
    windows = []

    while current < end:
        window_end = current + timedelta(days=1)

        if window_end > end:
            window_end = end

        windows.append((current, window_end))

        current = window_end

    return windows


def backfill(days):
    start, end = get_backfill_range(days)
    return get_daily_windows(start, end)

