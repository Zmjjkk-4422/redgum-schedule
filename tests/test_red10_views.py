"""Web flow tests for tutor-upcoming and student history views (RED-10)."""
from datetime import date, timedelta

from app import models


def _book(student, tutor, when, start="16:00", length="60", subject="Physics",
          status="booked"):
    return models.insert_session(
        {"student_id": student["id"], "tutor_id": tutor["id"], "subject": subject,
         "session_date": when.isoformat(), "start_time": start, "length_minutes": length},
        status=status,
    )


def test_tutor_upcoming_shows_future_not_past(client, tutor_with_windows, active_student):
    today = date.today()
    _book(active_student, tutor_with_windows, today + timedelta(days=3), start="16:00")
    _book(active_student, tutor_with_windows, today - timedelta(days=3), start="16:00")
    resp = client.get(f"/schedule/tutor/{tutor_with_windows['id']}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert (today + timedelta(days=3)).isoformat() in body
    assert (today - timedelta(days=3)).isoformat() not in body


def test_tutor_upcoming_empty_state(client, tutor_with_windows, active_student):
    resp = client.get(f"/schedule/tutor/{tutor_with_windows['id']}")
    assert resp.status_code == 200
    assert "No upcoming" in resp.get_data(as_text=True)


def test_tutor_upcoming_cancelled_marked(client, tutor_with_windows, active_student):
    future = date.today() + timedelta(days=2)
    _book(active_student, tutor_with_windows, future, status="cancelled")
    resp = client.get(f"/schedule/tutor/{tutor_with_windows['id']}")
    body = resp.get_data(as_text=True)
    assert future.isoformat() in body
    assert "cancelled" in body


def test_student_detail_splits_upcoming_and_past(client, tutor_with_windows, active_student):
    today = date.today()
    _book(active_student, tutor_with_windows, today + timedelta(days=4))
    _book(active_student, tutor_with_windows, today - timedelta(days=4))
    resp = client.get(f"/students/{active_student['id']}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Upcoming sessions" in body
    assert "Past sessions" in body
    assert (today + timedelta(days=4)).isoformat() in body
    assert (today - timedelta(days=4)).isoformat() in body


def test_student_cancelled_marked_in_history(client, tutor_with_windows, active_student):
    past = date.today() - timedelta(days=1)
    _book(active_student, tutor_with_windows, past, status="cancelled")
    resp = client.get(f"/students/{active_student['id']}")
    assert "cancelled" in resp.get_data(as_text=True)
