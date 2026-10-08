"""Scheduling service: create, move, cancel and update session status."""
from datetime import datetime

from flask import current_app

from .. import models
from .availability import AvailabilityError, validate_booking


class SchedulingError(ValueError):
    """Raised when a session command is invalid for non-availability reasons."""


# Centre-wide default weekly cap (RED-13). A tutor may set their own
# max_sessions_week on the tutor record, which overrides this default.
DEFAULT_WEEKLY_CAP = 12


def _check_weekly_cap(tutor, date_text, exclude_session_id=None):
    """Refuse when the tutor already has their weekly session cap for the
    ISO week (Mon-Sun) of date_text. Cancelled sessions do not count; the
    moved session itself is excluded so a move within the same week still
    occupies exactly one slot."""
    monday, sunday = models.iso_week_bounds(date_text)
    existing = models.count_tutor_active_sessions(
        tutor["id"], monday, sunday, exclude_session_id
    )
    cap = tutor["max_sessions_week"] or DEFAULT_WEEKLY_CAP
    if existing + 1 > cap:
        raise SchedulingError(
            f"{tutor['name']} already has {existing} session(s) in the week of "
            f"{monday.isoformat()} to {sunday.isoformat()}; the weekly cap is "
            f"{cap}. Choose a slot in another week, or move an existing session "
            "out of this week."
        )


def _check_overlap(student, tutor, date_text, start_time, length,
                   exclude_session_id=None):
    """RED-14: refuse when the SAME tutor already has an active session with
    this student that overlaps the requested slot. Touching boundaries
    (one ends exactly when the other starts) are allowed; cancelled sessions
    are ignored. The moved session itself is excluded from the check."""
    start_minutes = models.to_minutes(start_time)
    clash = models.find_overlapping_session(
        student["id"], tutor["id"], date_text,
        start_minutes, length, exclude_session_id,
    )
    if clash is not None:
        clash_start = models.to_minutes(clash["start_time"])
        clash_end_min = clash_start + clash["length_minutes"]
        clash_end = f"{clash_end_min // 60:02d}:{clash_end_min % 60:02d}"
        raise SchedulingError(
            f"{tutor['name']} already has a session with {student['name']} on "
            f"{date_text} from {clash['start_time']} to {clash_end}. Pick a "
            "non-overlapping slot (back-to-back sessions are allowed)."
        )


def _parse_date(date_text):
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise SchedulingError("Session date must be a valid date (YYYY-MM-DD).")


def _validate_common(data):
    """Validate fields shared by create and move; return normalised values."""
    errors = []
    student = models.get_student(data.get("student_id"))
    tutor = models.get_tutor(data.get("tutor_id"))
    if student is None:
        errors.append("Please choose a student.")
    elif student["status"] != "active":
        errors.append(f"{student['name']} is inactive and cannot be booked.")
    if tutor is None:
        errors.append("Please choose a tutor.")

    date_text = (data.get("session_date") or "").strip()
    try:
        _parse_date(date_text)
    except SchedulingError as exc:
        errors.append(str(exc))

    start_time = models.normalise_time(data.get("start_time"))
    if start_time is None:
        errors.append("Start time must be in HH:MM 24-hour format.")

    try:
        length = int(data.get("length_minutes"))
    except (TypeError, ValueError):
        length = None
    allowed = current_app.config["SESSION_LENGTHS"]
    if length not in allowed:
        errors.append(f"Session length must be one of: {', '.join(map(str, allowed))} minutes.")

    return student, tutor, date_text, start_time, length, errors


def create_session(data):
    """Create a booked session after full validation.

    Returns (session, errors). Availability failures are returned in errors
    so the UI can flash the reason rather than crash.
    """
    student, tutor, date_text, start_time, length, errors = _validate_common(data)
    if errors:
        return None, errors

    weekday = models.weekday_of(date_text)
    try:
        validate_booking(tutor, weekday, start_time, length)
    except AvailabilityError as exc:
        return None, [str(exc)]

    try:
        _check_weekly_cap(tutor, date_text)
    except SchedulingError as exc:
        return None, [str(exc)]

    try:
        _check_overlap(student, tutor, date_text, start_time, length)
    except SchedulingError as exc:
        return None, [str(exc)]

    payload = dict(data)
    payload["session_date"] = date_text
    payload["start_time"] = start_time
    payload["length_minutes"] = length
    return models.insert_session(payload, status="booked"), []


def move_session(session_id, new_date, new_start, new_length=None):
    """Move (reschedule) a session. The availability rule is re-checked;
    moving one session never changes any other session."""
    session = models.get_session(session_id)
    if session is None:
        raise SchedulingError("That session does not exist.")
    if session["status"] == "cancelled":
        raise SchedulingError("A cancelled session cannot be moved; book a new session instead.")

    data = {
        "student_id": session["student_id"],
        "tutor_id": session["tutor_id"],
        "session_date": new_date,
        "start_time": new_start,
        "length_minutes": new_length or session["length_minutes"],
    }
    student, tutor, date_text, start_time, length, errors = _validate_common(data)
    if errors:
        raise SchedulingError(" ".join(errors))

    weekday = models.weekday_of(date_text)
    validate_booking(tutor, weekday, start_time, length)
    _check_weekly_cap(tutor, date_text, exclude_session_id=session_id)
    _check_overlap(student, tutor, date_text, start_time, length,
                   exclude_session_id=session_id)

    from ..db import get_db

    db = get_db()
    db.execute(
        "UPDATE sessions SET session_date=?, start_time=?, length_minutes=? WHERE id=?",
        (date_text, start_time, length, session_id),
    )
    db.commit()
    return models.get_session(session_id)


def cancel_session(session_id):
    """Cancel a session. The record is retained and stays visible."""
    session = models.get_session(session_id)
    if session is None:
        raise SchedulingError("That session does not exist.")
    from ..db import get_db

    db = get_db()
    db.execute("UPDATE sessions SET status='cancelled' WHERE id=?", (session_id,))
    db.commit()
    return models.get_session(session_id)


def mark_session_status(session_id, status):
    """Mark a booked session attended or missed (cancelled stays cancelled)."""
    if status not in ("attended", "missed"):
        raise SchedulingError("Status can only be set to attended or missed here.")
    session = models.get_session(session_id)
    if session is None:
        raise SchedulingError("That session does not exist.")
    if session["status"] == "cancelled":
        raise SchedulingError("A cancelled session cannot be marked attended or missed.")
    from ..db import get_db

    db = get_db()
    db.execute("UPDATE sessions SET status=? WHERE id=?", (status, session_id))
    db.commit()
    return models.get_session(session_id)
