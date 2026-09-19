"""Tests for tutor records, availability windows and deactivation (RED-05/06)."""
from app import models
from app.services.scheduling import cancel_session, create_session


def test_create_tutor_persists(ctx):
    tutor, errors = models.create_tutor(
        {"name": "Tomas Ferreira", "subjects": "Physics, Chemistry", "max_sessions_week": "8"}
    )
    assert errors == []
    assert models.get_tutor(tutor["id"])["max_sessions_week"] == 8


def test_tutor_requires_name_and_subjects(ctx):
    tutor, errors = models.create_tutor({"name": "", "subjects": ""})
    assert tutor is None
    assert len(errors) == 2


def test_window_time_validation(ctx):
    tutor, _ = models.create_tutor({"name": "Bad Window Tutor", "subjects": "Maths"})
    assert models.add_window(tutor["id"], {"weekday": "2", "start_time": "18:00", "end_time": "17:00"})
    assert models.add_window(tutor["id"], {"weekday": "2", "start_time": "banana", "end_time": "18:00"})
    assert models.add_window(tutor["id"], {"weekday": "9", "start_time": "09:00", "end_time": "10:00"})
    assert models.list_windows(tutor["id"]) == []


def test_window_add_and_delete(ctx):
    tutor, _ = models.create_tutor({"name": "Window Tutor", "subjects": "Maths"})
    assert models.add_window(
        tutor["id"], {"weekday": "6", "start_time": "9:00", "end_time": "12:30", "note": "x"}
    ) == []
    windows = models.list_windows(tutor["id"])
    assert len(windows) == 1
    assert windows[0]["start_time"] == "09:00"  # normalised
    models.delete_window(windows[0]["id"])
    assert models.list_windows(tutor["id"]) == []


def test_deactivated_tutor_keeps_session_history(tutor_with_windows, active_student):
    session, _ = create_session(
        {"student_id": active_student["id"], "tutor_id": tutor_with_windows["id"],
         "subject": "Physics", "session_date": "2026-09-15", "start_time": "16:00",
         "length_minutes": 60}
    )
    cancel_session(session["id"])
    models.set_tutor_status(tutor_with_windows["id"], "inactive")
    assert all(t["id"] != tutor_with_windows["id"] for t in models.list_tutors(active_only=True))
    history = models.list_sessions(tutor_id=tutor_with_windows["id"])
    assert len(history) == 1
    assert history[0]["status"] == "cancelled"
