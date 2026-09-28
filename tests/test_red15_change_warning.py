"""RED-15: warning when availability changes strand existing bookings."""
from datetime import date, timedelta

from app import models


def _next_weekday(from_date, target):
    """Return the next date (on/after from_date) whose isoweekday == target (Mon=1)."""
    days = (target - from_date.isoweekday()) % 7
    return from_date + timedelta(days=days)


def _book(tutor, student, when, start="16:00", length="60"):
    return models.insert_session(
        {"student_id": student["id"], "tutor_id": tutor["id"], "subject": "Physics",
         "session_date": when.isoformat(), "start_time": start, "length_minutes": length},
        status="booked",
    )


def _tuesday():
    return _next_weekday(date.today(), 2)  # Tomas has Tue 15:30-19:00 window


def test_stranded_session_flagged_after_window_removed(client, tutor_with_windows, active_student):
    tue = _tuesday()
    _book(tutor_with_windows, active_student, tue, start="16:00")
    # sanity: fits before removal
    assert "no longer fit" not in client.get(
        f"/tutors/{tutor_with_windows['id']}/availability").get_data(as_text=True)

    # remove the Tuesday window
    tue_window = next(w for w in models.list_windows(tutor_with_windows["id"]) if w["weekday"] == 2)
    models.delete_window(tue_window["id"])

    resp = client.get(f"/tutors/{tutor_with_windows['id']}/availability")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "no longer fit" in body
    assert tue.isoformat() in body
    assert "Kai Lombardo" in body


def test_session_never_deleted(client, tutor_with_windows, active_student):
    tue = _tuesday()
    sess = _book(tutor_with_windows, active_student, tue, start="16:00")
    tue_window = next(w for w in models.list_windows(tutor_with_windows["id"]) if w["weekday"] == 2)
    models.delete_window(tue_window["id"])
    # record still exists and remains booked
    assert models.get_session(sess["id"])["status"] == "booked"


def test_session_still_covered_not_flagged(client, tutor_with_windows, active_student):
    # book on Wednesday (weekday 3, 15:30-18:00); remove Tuesday window only
    wed = _next_weekday(date.today(), 3)
    _book(tutor_with_windows, active_student, wed, start="16:00")
    tue_window = next(w for w in models.list_windows(tutor_with_windows["id"]) if w["weekday"] == 2)
    models.delete_window(tue_window["id"])
    body = client.get(
        f"/tutors/{tutor_with_windows['id']}/availability").get_data(as_text=True)
    assert "All booked sessions still fit" in body


def test_re_add_window_restores_all_clear(client, tutor_with_windows, active_student):
    tue = _tuesday()
    _book(tutor_with_windows, active_student, tue, start="16:00")
    tue_window = next(w for w in models.list_windows(tutor_with_windows["id"]) if w["weekday"] == 2)
    models.delete_window(tue_window["id"])
    # re-add the Tuesday window
    models.add_window(tutor_with_windows["id"],
                      {"weekday": "2", "start_time": "15:30", "end_time": "19:00", "note": ""})
    body = client.get(
        f"/tutors/{tutor_with_windows['id']}/availability").get_data(as_text=True)
    assert "All booked sessions still fit" in body
