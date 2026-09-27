"""Web flow tests for booking sessions (RED-07) and move/cancel/status (RED-08)."""
from app import models
from app.services.scheduling import create_session


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


def test_book_90min_running_past_window_close_refused(client, tutor_with_windows, active_student):
    # Tuesday window ends 19:00; 18:00 + 90 min ends 19:30 -> must be refused.
    resp = client.post(
        "/sessions/book",
        data=_form(active_student, tutor_with_windows, start="18:00", length="90"),
    )
    assert resp.status_code == 200
    assert models.count_sessions() == 0


def test_deactivated_student_and_tutor_not_in_selects(client, tutor_with_windows, active_student):
    models.set_student_status(active_student["id"], "inactive")
    models.set_tutor_status(tutor_with_windows["id"], "inactive")
    resp = client.get("/sessions/book")
    body = resp.get_data(as_text=True)
    assert active_student["name"] not in body
    assert tutor_with_windows["name"] not in body


# ------------------------------------------------------------ RED-08 move
def test_move_form_renders_session_details(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    resp = client.get(f"/sessions/{session['id']}/move")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Move session" in body
    assert active_student["name"] in body
    assert tutor_with_windows["name"] in body


def test_move_valid_redirects_and_updates(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    resp = client.post(
        f"/sessions/{session['id']}/move",
        data={"session_date": "2026-09-19", "start_time": "09:00", "length_minutes": "90"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/sessions/?date=2026-09-19" in resp.headers["Location"]
    moved = models.get_session(session["id"])
    assert moved["session_date"] == "2026-09-19"
    assert moved["start_time"] == "09:00"
    assert moved["length_minutes"] == 90
    assert moved["status"] == "booked"


def test_move_outside_window_refused_and_unchanged(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    resp = client.post(
        f"/sessions/{session['id']}/move",
        data={"session_date": "2026-09-18", "start_time": "10:00", "length_minutes": "60"},
    )
    assert resp.status_code == 200  # form re-rendered with the reason
    body = resp.get_data(as_text=True)
    unchanged = models.get_session(session["id"])
    assert unchanged["session_date"] == "2026-09-15"
    assert unchanged["start_time"] == "16:00"
    assert "window" in body.lower() or "availability" in body.lower()


def test_move_cancelled_session_refused(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    client.post(f"/sessions/{session['id']}/cancel")
    resp = client.post(
        f"/sessions/{session['id']}/move",
        data={"session_date": "2026-09-19", "start_time": "09:00", "length_minutes": "60"},
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "cancelled session cannot be moved" in body.lower()
    assert models.get_session(session["id"])["status"] == "cancelled"


# ----------------------------------------------------------- RED-08 cancel
def test_cancel_marks_cancelled_and_keeps_record(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    resp = client.post(f"/sessions/{session['id']}/cancel", follow_redirects=False)
    assert resp.status_code == 302
    reloaded = models.get_session(session["id"])
    assert reloaded["status"] == "cancelled"
    assert models.count_sessions() == 1  # record retained, still visible


# ------------------------------------------------------------ RED-08 status
def test_mark_attended_and_missed(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    client.post(f"/sessions/{session['id']}/status", data={"status": "attended"})
    assert models.get_session(session["id"])["status"] == "attended"
    other, _ = create_session(_form(active_student, tutor_with_windows, start="17:00"))
    client.post(f"/sessions/{other['id']}/status", data={"status": "missed"})
    assert models.get_session(other["id"])["status"] == "missed"


def test_cancelled_cannot_be_marked(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    client.post(f"/sessions/{session['id']}/cancel")
    resp = client.post(f"/sessions/{session['id']}/status", data={"status": "attended"})
    assert resp.status_code == 302
    assert models.get_session(session["id"])["status"] == "cancelled"


def test_status_rejects_unknown_value(client, tutor_with_windows, active_student):
    session, _ = create_session(_form(active_student, tutor_with_windows))
    resp = client.post(f"/sessions/{session['id']}/status", data={"status": "bogus"})
    assert resp.status_code == 302
    assert models.get_session(session["id"])["status"] == "booked"
