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
