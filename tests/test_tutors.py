"""Tests for tutor records and deactivation history (RED-05)."""
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
