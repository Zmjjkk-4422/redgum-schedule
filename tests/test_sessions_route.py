"""Web flow tests for booking a session (RED-07)."""
from app import models


def _form(student, tutor, date="2026-09-15", start="16:00", length="60", subject="Physics"):
    # 2026-09-15 is a Tuesday; the tutor window is 15:30-19:00.
    return {
        "student_id": str(student["id"]),
        "tutor_id": str(tutor["id"]),
        "subject": subject,
        "session_date": date,
        "start_time": start,
        "length_minutes": length,
    }


def test_book_form_lists_only_active(client, tutor_with_windows, active_student):
    resp = client.get("/sessions/book")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Book a session" in body
    assert active_student["name"] in body
    assert tutor_with_windows["name"] in body


def test_book_valid_redirects_and_saves_booked(client, tutor_with_windows, active_student):
    resp = client.post(
        "/sessions/book",
        data=_form(active_student, tutor_with_windows),
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/sessions/?date=2026-09-15" in resp.headers["Location"]
    session = models.list_sessions()[0]
    assert session["status"] == "booked"


def test_book_outside_window_refused_and_nothing_saved(client, tutor_with_windows, active_student):
    resp = client.post(
        "/sessions/book",
        data=_form(active_student, tutor_with_windows, start="14:00"),
    )
    assert resp.status_code == 200  # form re-rendered with the reason
    body = resp.get_data(as_text=True)
    assert models.count_sessions() == 0
    assert "before" in body.lower() or "availability" in body.lower()


def test_book_missing_student_and_tutor_are_named(client, tutor_with_windows, active_student):
    form = _form(active_student, tutor_with_windows)
    form["student_id"] = ""
    form["tutor_id"] = ""
    resp = client.post("/sessions/book", data=form)
    assert resp.status_code == 200
    assert models.count_sessions() == 0


def test_book_rejects_bad_length(client, tutor_with_windows, active_student):
    resp = client.post(
        "/sessions/book",
        data=_form(active_student, tutor_with_windows, length="45"),
    )
    assert resp.status_code == 200
    assert models.count_sessions() == 0


def test_booked_session_appears_on_day_list(client, tutor_with_windows, active_student):
    client.post("/sessions/book", data=_form(active_student, tutor_with_windows))
    resp = client.get("/sessions/?date=2026-09-15")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert active_student["name"] in body
    assert "booked" in body
