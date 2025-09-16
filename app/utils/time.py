"""Time utilities for CityPulse backend."""
from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def expires_in_24h() -> datetime:
    """Get expiration time 24 hours from now."""
    return utcnow() + timedelta(hours=24)


def hours_ago(hours: int) -> datetime:
    """Get time N hours ago."""
    return utcnow() - timedelta(hours=hours)


def format_time_ago(dt: datetime) -> str:
    """Format datetime as human-readable 'time ago' string."""
    now = utcnow()

    # Handle timezone-naive datetimes
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt

    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "just now"


def is_expired(expires_at: datetime) -> bool:
    """Check if a timestamp has expired."""
    now = utcnow()

    # Handle timezone-naive datetimes
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    return now >= expires_at