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


def backfill(days=None, start=None, end=None):
    if days is not None and (start is not None or end is not None):
        raise ValueError("Provide either days or start and end, not both.")
    elif start is not None and end is not None:
        pass
    elif days is not None:
        start, end = get_backfill_range(days)
    else:
        raise ValueError("Provide either days or both start and end.")

    return get_daily_windows(start, end)

