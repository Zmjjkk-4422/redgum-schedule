"""Tutor availability domain rule (the centre's core business rule).

A session may only be booked, or moved, when it falls ENTIRELY inside one of
that tutor's availability windows for the weekday of the session date.
Invalid bookings are refused with a plain-language reason; they are never
accepted silently.
"""
from ..models import (
    WEEKDAY_NAMES,
    to_minutes,
    windows_for_weekday,
)


class AvailabilityError(ValueError):
    """Raised when a proposed booking cannot fit any availability window."""


def find_fitting_window(tutor_id, weekday, start_time, length_minutes):
    """Return the availability window that fully contains the proposed slot,
    or None when no window contains it."""
    start = to_minutes(start_time)
    end = start + int(length_minutes)
    for window in windows_for_weekday(tutor_id, weekday):
        if (
            to_minutes(window["start_time"]) <= start
            and to_minutes(window["end_time"]) >= end
        ):
            return window
    return None


def validate_booking(tutor, weekday, start_time, length_minutes):
    """Validate a proposed booking against the tutor's windows.

    Returns the fitting window. Raises AvailabilityError with a specific,
    user-facing reason otherwise.
    """
    if tutor is None:
        raise AvailabilityError("Please choose a tutor.")
    if tutor["status"] != "active":
        raise AvailabilityError(
            f"{tutor['name']} is deactivated and cannot take new bookings."
        )

    day_name = WEEKDAY_NAMES.get(weekday, "that day")
    windows = windows_for_weekday(tutor["id"], weekday)
    if not windows:
        raise AvailabilityError(
            f"{tutor['name']} has no availability window on {day_name}s, "
            "so the session cannot be booked."
        )

    fitting = find_fitting_window(tutor["id"], weekday, start_time, length_minutes)
    if fitting is not None:
        return fitting

    start = to_minutes(start_time)
    end = start + int(length_minutes)
    earliest = min(to_minutes(w["start_time"]) for w in windows)
    latest = max(to_minutes(w["end_time"]) for w in windows)
    if start < earliest:
        raise AvailabilityError(
            f"The session starts before {tutor['name']}'s first availability "
            f"window on {day_name} opens ({windows[0]['start_time']})."
        )
    if end > latest:
        last_window = max(windows, key=lambda w: to_minutes(w["end_time"]))
        raise AvailabilityError(
            f"The {length_minutes}-minute session runs past {tutor['name']}'s "
            f"last availability window on {day_name} (closes "
            f"{last_window['end_time']}); choose an earlier start or a shorter "
            "session."
        )
    raise AvailabilityError(
        f"The session does not fall entirely inside any of {tutor['name']}'s "
        f"availability windows on {day_name}. Available windows: "
        + "; ".join(f"{w['start_time']}\u2013{w['end_time']}" for w in windows)
        + "."
    )
