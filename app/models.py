"""Repository layer: students, tutors, availability windows and sessions.

Each create/update function validates required fields and returns
(record, errors). When errors is non-empty the record was NOT saved, which
lets the UI name the missing field instead of storing bad data.
"""
import re
from datetime import datetime

from .db import get_db

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d$")
WEEKDAY_NAMES = {
    1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
    5: "Friday", 6: "Saturday", 7: "Sunday",
}


def to_minutes(value):
    """Convert HH:MM to minutes since midnight."""
    hour, minute = (int(x) for x in value.split(":"))
    return hour * 60 + minute


def normalise_time(value):
    """Normalise H:MM to HH:MM; return None when the value is malformed."""
    value = (value or "").strip()
    if not TIME_RE.match(value):
        return None
    hour, minute = value.split(":")
    return f"{int(hour):02d}:{minute}"


def weekday_of(date_text):
    """ISO weekday (1=Monday ... 7=Sunday) for a YYYY-MM-DD date."""
    return datetime.strptime(date_text, "%Y-%m-%d").isoweekday()


# ---------------------------------------------------------------- students
def list_students(active_only=False):
    sql = "SELECT * FROM students"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY name"
    return get_db().execute(sql).fetchall()


def get_student(student_id):
    return get_db().execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()


def count_students():
    return get_db().execute("SELECT COUNT(*) FROM students").fetchone()[0]


def validate_student(data):
    errors = []
    if not str(data.get("name") or "").strip():
        errors.append("Student name is required.")
    year = str(data.get("year_level") or "").strip()
    if not year:
        errors.append("Year level is required.")
    elif not year.isdigit() or not 5 <= int(year) <= 12:
        errors.append("Year level must be a number between 5 and 12.")
    if not (data.get("contact_phone") or "").strip() and not (
        data.get("contact_email") or ""
    ).strip():
        errors.append("At least one family contact (phone or email) is required.")
    return errors


def create_student(data):
    errors = validate_student(data)
    if errors:
        return None, errors
    db = get_db()
    cur = db.execute(
        """INSERT INTO students
           (name, year_level, contact_name, contact_phone, contact_email, subjects)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            data["name"].strip(),
            int(data["year_level"]),
            data.get("contact_name", "").strip(),
            data.get("contact_phone", "").strip(),
            data.get("contact_email", "").strip(),
            data.get("subjects", "").strip(),
        ),
    )
    db.commit()
    return get_student(cur.lastrowid), []


def update_student(student_id, data):
    errors = validate_student(data)
    if errors:
        return errors
    db = get_db()
    db.execute(
        """UPDATE students SET name=?, year_level=?, contact_name=?,
           contact_phone=?, contact_email=?, subjects=? WHERE id=?""",
        (
            data["name"].strip(),
            int(data["year_level"]),
            data.get("contact_name", "").strip(),
            data.get("contact_phone", "").strip(),
            data.get("contact_email", "").strip(),
            data.get("subjects", "").strip(),
            student_id,
        ),
    )
    db.commit()
    return []


def set_student_status(student_id, status):
    db = get_db()
    db.execute("UPDATE students SET status=? WHERE id=?", (status, student_id))
    db.commit()


# ----------------------------------------------------------------- tutors
def list_tutors(active_only=False):
    sql = "SELECT * FROM tutors"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY name"
    return get_db().execute(sql).fetchall()


def get_tutor(tutor_id):
    return get_db().execute(
        "SELECT * FROM tutors WHERE id = ?", (tutor_id,)
    ).fetchone()


def count_tutors():
    return get_db().execute("SELECT COUNT(*) FROM tutors").fetchone()[0]


def validate_tutor(data):
    errors = []
    if not (data.get("name") or "").strip():
        errors.append("Tutor name is required.")
    if not (data.get("subjects") or "").strip():
        errors.append("At least one subject taught is required.")
    return errors


def create_tutor(data):
    errors = validate_tutor(data)
    if errors:
        return None, errors
    max_week = (data.get("max_sessions_week") or "").strip()
    db = get_db()
    cur = db.execute(
        "INSERT INTO tutors (name, subjects, max_sessions_week) VALUES (?, ?, ?)",
        (
            data["name"].strip(),
            data.get("subjects", "").strip(),
            int(max_week) if max_week.isdigit() else None,
        ),
    )
    db.commit()
    return get_tutor(cur.lastrowid), []


def update_tutor(tutor_id, data):
    errors = validate_tutor(data)
    if errors:
        return errors
    max_week = (data.get("max_sessions_week") or "").strip()
    db = get_db()
    db.execute(
        "UPDATE tutors SET name=?, subjects=?, max_sessions_week=? WHERE id=?",
        (
            data["name"].strip(),
            data.get("subjects", "").strip(),
            int(max_week) if max_week.isdigit() else None,
            tutor_id,
        ),
    )
    db.commit()
    return []


def set_tutor_status(tutor_id, status):
    """Deactivated tutors keep their historical sessions but disappear from
    new-booking options."""
    db = get_db()
    db.execute("UPDATE tutors SET status=? WHERE id=?", (status, tutor_id))
    db.commit()


# --------------------------------------------------- availability windows
def list_windows(tutor_id=None):
    sql = "SELECT * FROM availability_windows"
    params = ()
    if tutor_id is not None:
        sql += " WHERE tutor_id = ?"
        params = (tutor_id,)
    sql += " ORDER BY tutor_id, weekday, start_time"
    return get_db().execute(sql, params).fetchall()


def windows_for_weekday(tutor_id, weekday):
    return get_db().execute(
        "SELECT * FROM availability_windows WHERE tutor_id=? AND weekday=? "
        "ORDER BY start_time",
        (tutor_id, weekday),
    ).fetchall()


def get_window(window_id):
    return get_db().execute(
        "SELECT * FROM availability_windows WHERE id=?", (window_id,)
    ).fetchone()


def validate_window(data):
    errors = []
    weekday = str(data.get("weekday") or "").strip()
    if not weekday.isdigit() or not 1 <= int(weekday) <= 7:
        errors.append("Weekday must be between 1 (Monday) and 7 (Sunday).")
    start = normalise_time(data.get("start_time"))
    end = normalise_time(data.get("end_time"))
    if start is None:
        errors.append("Start time must be in HH:MM 24-hour format.")
    if end is None:
        errors.append("End time must be in HH:MM 24-hour format.")
    if start and end and to_minutes(end) <= to_minutes(start):
        errors.append("End time must be later than start time.")
    return errors, start, end


def add_window(tutor_id, data):
    errors, start, end = validate_window(data)
    if errors:
        return errors
    db = get_db()
    db.execute(
        "INSERT INTO availability_windows (tutor_id, weekday, start_time, end_time, note)"
        " VALUES (?, ?, ?, ?, ?)",
        (
            tutor_id,
            int(data["weekday"]),
            start,
            end,
            data.get("note", "").strip(),
        ),
    )
    db.commit()
    return []


def delete_window(window_id):
    db = get_db()
    db.execute("DELETE FROM availability_windows WHERE id=?", (window_id,))
    db.commit()


# ---------------------------------------------------------------- sessions
def list_sessions(date=None, tutor_id=None, student_id=None, include_cancelled=True):
    clauses, params = [], []
    if date is not None:
        if isinstance(date, tuple):  # (start_date, end_date) inclusive
            clauses.append("session_date BETWEEN ? AND ?")
            params.extend(date)
        else:
            clauses.append("session_date = ?")
            params.append(date)
    if tutor_id is not None:
        clauses.append("tutor_id = ?")
        params.append(tutor_id)
    if student_id is not None:
        clauses.append("student_id = ?")
        params.append(student_id)
    if not include_cancelled:
        clauses.append("status != 'cancelled'")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return get_db().execute(
        f"""SELECT s.*, st.name AS student_name, t.name AS tutor_name
            FROM sessions s
            JOIN students st ON st.id = s.student_id
            JOIN tutors t ON t.id = s.tutor_id
            {where}
            ORDER BY session_date, start_time""",
        params,
    ).fetchall()


def get_session(session_id):
    return get_db().execute(
        """SELECT s.*, st.name AS student_name, t.name AS tutor_name
           FROM sessions s
           JOIN students st ON st.id = s.student_id
           JOIN tutors t ON t.id = s.tutor_id
           WHERE s.id=?""",
        (session_id,),
    ).fetchone()


def count_sessions():
    return get_db().execute("SELECT COUNT(*) FROM sessions").fetchone()[0]


def insert_session(data, status="booked"):
    """Internal insert used by the scheduling service and seed data."""
    db = get_db()
    cur = db.execute(
        """INSERT INTO sessions
           (student_id, tutor_id, subject, session_date, start_time,
            length_minutes, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data["student_id"],
            data["tutor_id"],
            data.get("subject", "").strip(),
            data["session_date"],
            data["start_time"],
            int(data["length_minutes"]),
            status,
        ),
    )
    db.commit()
    return get_session(cur.lastrowid)
