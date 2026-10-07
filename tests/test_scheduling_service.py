"""Tests for the scheduling service: create, move, cancel, status (RED-07/08)."""
import pytest

from app import models
from app.services.availability import AvailabilityError
from app.services.scheduling import (
    SchedulingError,
    cancel_session,
    create_session,
    mark_session_status,
    move_session,
)


def _data(student, tutor, date="2026-09-15", start="16:00", length=60, subject="Physics"):
    # 2026-09-15 is a Tuesday; tutor window is 15:30-19:00.
    return {
        "student_id": student["id"],
        "tutor_id": tutor["id"],
        "subject": subject,
        "session_date": date,
        "start_time": start,
        "length_minutes": length,
    }


def test_create_valid_session_is_booked(tutor_with_windows, active_student):
    session, errors = create_session(_data(active_student, tutor_with_windows))
    assert errors == []
    assert session["status"] == "booked"
    assert models.count_sessions() == 1


def test_create_outside_window_returns_reason(tutor_with_windows, active_student):
    data = _data(active_student, tutor_with_windows, start="14:00")
    session, errors = create_session(data)
    assert session is None
    assert any("before" in e for e in errors)


def test_create_rejects_bad_length(tutor_with_windows, active_student):
    session, errors = create_session(_data(active_student, tutor_with_windows, length=45))
    assert session is None
    assert any("60" in e and "90" in e for e in errors)


def test_create_rejects_inactive_student(tutor_with_windows, active_student):
    models.set_student_status(active_student["id"], "inactive")
    session, errors = create_session(_data(active_student, tutor_with_windows))
    assert session is None
    assert any("inactive" in e for e in errors)


def test_cancel_keeps_record_visible(tutor_with_windows, active_student):
    session, _ = create_session(_data(active_student, tutor_with_windows))
    cancelled = cancel_session(session["id"])
    assert cancelled["status"] == "cancelled"
    assert models.get_session(session["id"]) is not None
    assert len(models.list_sessions()) == 1


def test_move_revalidates_availability(tutor_with_windows, active_student):
    # Tuesday 16:00 -> Saturday 11:00 (90 minutes, inside 09:00-12:30).
    session, _ = create_session(_data(active_student, tutor_with_windows))
    moved = move_session(session["id"], "2026-09-19", "11:00", 90)
    assert moved["session_date"] == "2026-09-19"
    assert moved["start_time"] == "11:00"
    assert moved["length_minutes"] == 90


def test_move_into_invalid_slot_refused(tutor_with_windows, active_student):
    session, _ = create_session(_data(active_student, tutor_with_windows))
    with pytest.raises(AvailabilityError):
        move_session(session["id"], "2026-09-18", "10:00", 60)  # Friday, no window
    unchanged = models.get_session(session["id"])
    assert unchanged["session_date"] == "2026-09-15"


def test_moving_one_session_does_not_change_another(tutor_with_windows, active_student):
    first, _ = create_session(_data(active_student, tutor_with_windows, start="16:00"))
    second_student, _ = models.create_student(
        {"name": "Ella Nguyen", "year_level": "11", "contact_phone": "0400 000 000",
         "subjects": "Physics"}
    )
    second, _ = create_session(_data(second_student, tutor_with_windows, start="17:00"))
    move_session(first["id"], "2026-09-19", "09:00", 60)
    second_reloaded = models.get_session(second["id"])
    assert second_reloaded["session_date"] == "2026-09-15"
    assert second_reloaded["start_time"] == "17:00"


def test_status_lifecycle(tutor_with_windows, active_student):
    session, _ = create_session(_data(active_student, tutor_with_windows))
    assert mark_session_status(session["id"], "attended")["status"] == "attended"
    other, _ = create_session(_data(active_student, tutor_with_windows, start="17:00"))
    assert mark_session_status(other["id"], "missed")["status"] == "missed"
    cancelled = cancel_session(other["id"])
    with pytest.raises(SchedulingError):
        mark_session_status(cancelled["id"], "attended")
    with pytest.raises(SchedulingError):
        move_session(cancelled["id"], "2026-09-19", "09:00", 60)


# ------------------------------------------------------------- RED-13 weekly cap
# ISO week Mon 2026-09-14 .. Sun 2026-09-20; 60-min slots fitting Tomas's windows.
WEEK_SLOTS = [
    ("2026-09-15", "15:30"),  # Tue window 15:30-19:00
    ("2026-09-15", "16:30"),
    ("2026-09-15", "17:30"),
    ("2026-09-16", "15:30"),  # Wed window 15:30-18:00
    ("2026-09-16", "16:30"),
    ("2026-09-17", "16:00"),  # Thu window 16:00-18:30
    ("2026-09-17", "17:00"),
    ("2026-09-19", "09:00"),  # Sat window 09:00-12:30
]


def _book(student, tutor, date, start, length=60):
    session, errors = create_session(_data(student, tutor, date=date, start=start, length=length))
    assert errors == [], errors
    return session


def test_weekly_cap_refuses_ninth_booking_in_tomas_week(tutor_with_windows, active_student):
    # Tomas has max_sessions_week = 8; the 9th booking in one ISO week is refused.
    for date, start in WEEK_SLOTS:
        _book(active_student, tutor_with_windows, date, start)
    assert models.count_sessions() == 8
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-19", start="10:00")
    )
    assert session is None
    assert any("cap" in e.lower() for e in errors)


def test_cancelled_session_does_not_count_toward_cap(tutor_with_windows, active_student):
    for date, start in WEEK_SLOTS:
        _book(active_student, tutor_with_windows, date, start)
    # Cancelling one frees a slot, even though the record stays.
    cancel_session(models.list_sessions(date="2026-09-15")[0]["id"])
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-19", start="10:00")
    )
    assert errors == [], errors
    assert session is not None


def test_moving_into_full_week_refused_and_moving_out_frees_capacity(
    tutor_with_windows, active_student
):
    for date, start in WEEK_SLOTS:
        _book(active_student, tutor_with_windows, date, start)
    # A spare session in the NEXT week.
    spare = _book(active_student, tutor_with_windows, "2026-09-26", "09:00")
    # Moving it into the already-full week must be refused.
    with pytest.raises(SchedulingError):
        move_session(spare["id"], "2026-09-19", "10:00", 60)
    assert models.get_session(spare["id"])["session_date"] == "2026-09-26"
    # Moving one session OUT of the full week frees a slot.
    victim = models.list_sessions(date="2026-09-15")[0]
    move_session(victim["id"], "2026-09-26", "10:00", 60)
    # Now a booking in the previously-full week is accepted.
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-19", start="10:00")
    )
    assert errors == [], errors
    assert session is not None


def test_default_weekly_cap_is_twelve_without_tutor_limit(ctx, active_student):
    # A tutor without max_sessions_week falls back to the centre default (12),
    # which must be above Tomas's per-tutor limit of 8.
    tutor, _ = models.create_tutor(
        {"name": "Helen Vasquez", "subjects": "Math Methods", "max_sessions_week": ""}
    )
    for weekday, start, end in [
        (2, "15:30", "19:00"), (3, "15:30", "18:00"),
        (4, "16:00", "18:30"), (6, "09:00", "12:30"),
    ]:
        assert models.add_window(
            tutor["id"],
            {"weekday": str(weekday), "start_time": start, "end_time": end, "note": ""},
        ) == []
    for date, start in WEEK_SLOTS:
        _book(active_student, tutor, date, start)
    session, errors = create_session(
        _data(active_student, tutor, date="2026-09-19", start="10:00")
    )
    assert errors == [], errors
    assert session is not None


# ------------------------------------------------------------- RED-14 overlap guard
# Tuesday 2026-09-15, Tomas window 15:30-19:00.
def test_overlapping_same_tutor_student_booking_refused(tutor_with_windows, active_student):
    _book(active_student, tutor_with_windows, "2026-09-15", "16:00")
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-15", start="16:30")
    )
    assert session is None
    assert any("already has a session" in e for e in errors)


def test_touching_boundaries_are_allowed(tutor_with_windows, active_student):
    # 16:00-17:00 then 17:00-18:00: back-to-back, no overlap.
    _book(active_student, tutor_with_windows, "2026-09-15", "16:00")
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-15", start="17:00")
    )
    assert errors == [], errors
    assert session is not None


def test_overlap_guard_ignores_other_students(tutor_with_windows, active_student):
    # Same tutor, different student at the same time: not the RED-14 conflict.
    second, _ = models.create_student(
        {"name": "Ella Nguyen", "year_level": "11", "contact_phone": "0400 000 000",
         "subjects": "Physics"}
    )
    _book(active_student, tutor_with_windows, "2026-09-15", "16:00")
    session, errors = create_session(
        _data(second, tutor_with_windows, date="2026-09-15", start="16:30")
    )
    assert errors == [], errors
    assert session is not None


def test_overlap_guard_ignores_other_tutors(tutor_with_windows, active_student):
    # Same student, different tutor at the same time: not the RED-14 conflict.
    other_tutor, _ = models.create_tutor(
        {"name": "Helen Vasquez", "subjects": "Math Methods", "max_sessions_week": ""}
    )
    for weekday, start, end in [(2, "15:30", "19:00")]:
        assert models.add_window(
            other_tutor["id"],
            {"weekday": str(weekday), "start_time": start, "end_time": end, "note": ""},
        ) == []
    _book(active_student, tutor_with_windows, "2026-09-15", "16:00")
    session, errors = create_session(
        _data(active_student, other_tutor, date="2026-09-15", start="16:30")
    )
    assert errors == [], errors
    assert session is not None


def test_move_into_overlap_refused_but_touching_allowed(tutor_with_windows, active_student):
    _book(active_student, tutor_with_windows, "2026-09-15", "16:00")
    spare = _book(active_student, tutor_with_windows, "2026-09-26", "09:00")
    # Moving into 16:30-17:30 overlaps the 16:00-17:00 session -> refused.
    with pytest.raises(SchedulingError):
        move_session(spare["id"], "2026-09-15", "16:30", 60)
    assert models.get_session(spare["id"])["session_date"] == "2026-09-26"
    # Moving into 17:00-18:00 touches the boundary -> allowed.
    moved = move_session(spare["id"], "2026-09-15", "17:00", 60)
    assert moved["session_date"] == "2026-09-15"
    assert moved["start_time"] == "17:00"


def test_cancelled_session_does_not_block_booking(tutor_with_windows, active_student):
    first, _ = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-15", start="16:00")
    )
    cancel_session(first["id"])
    session, errors = create_session(
        _data(active_student, tutor_with_windows, date="2026-09-15", start="16:30")
    )
    assert errors == [], errors
    assert session is not None
