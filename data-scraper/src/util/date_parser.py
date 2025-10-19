from datetime import datetime, timezone
import time

def parse_last_updated(last_updated):
    formats = [
        "%a, %d %b %Y %H:%M:%S GMT",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(last_updated, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except ValueError:
            continue

    raise ValueError(f"Unrecognized date format: {last_updated}")