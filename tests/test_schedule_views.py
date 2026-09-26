"""Web flow tests for the centre day/week schedule view (RED-09)."""
from app import models


def _book(student, tutor, date="2026-09-15", start="16:00", length="60",
          subject="Physics", status="booked"):
    return models.insert_session(
        {"student_id": student["id"], "tutor_id": tutor["id"], "subject": subject,
         "session_date": date, "start_time": start, "length_minutes": length},
        status=status,
    )


def test_day_view_shows_session_on_its_date(client, tutor_with_windows, active_student):
    _book(active_student, tutor_with_windows, date="2026-09-15")
    resp = client.get("/schedule/?view=day&date=2026-09-15")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert active_student["name"] in body
    assert tutor_with_windows["name"] in body
    assert "16:00" in body


def test_day_view_empty_state(client, tutor_with_windows, active_student):
    resp = client.get("/schedule/?view=day&date=2026-09-15")
    assert resp.status_code == 200
    assert "No sessions" in resp.get_data(as_text=True)


def test_week_view_groups_sessions_across_days(client, tutor_with_windows, active_student):
    # Monday 2026-09-14 and Wednesday 2026-09-16 fall in ISO week of Mon 14 Sep.
    _book(active_student, tutor_with_windows, date="2026-09-14", start="16:00")
    _book(active_student, tutor_with_windows, date="2026-09-16", start="17:00")
    resp = client.get("/schedule/?view=week&date=2026-09-15")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "2026-09-14" in body
    assert "2026-09-16" in body


def test_week_view_excludes_sessions_outside_week(client, tutor_with_windows, active_student):
    # 2026-09-08 is the prior Monday; must not appear in the week of 14 Sep.
    _book(active_student, tutor_with_windows, date="2026-09-08", start="16:00")
    resp = client.get("/schedule/?view=week&date=2026-09-15")
    assert resp.status_code == 200
    assert "2026-09-08" not in resp.get_data(as_text=True)


def test_cancelled_session_visible_and_marked(client, tutor_with_windows, active_student):
    _book(active_student, tutor_with_windows, date="2026-09-15", status="cancelled")
    resp = client.get("/schedule/?view=day&date=2026-09-15")
    body = resp.get_data(as_text=True)
    assert active_student["name"] in body
    assert "cancelled" in body


def test_bad_date_falls_back_without_error(client):
    resp = client.get("/schedule/?view=day&date=not-a-date")
    assert resp.status_code == 200
