"""SQLite connection management and schema creation."""
import os
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    year_level INTEGER NOT NULL,
    contact_name TEXT,
    contact_phone TEXT,
    contact_email TEXT,
    subjects TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tutors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subjects TEXT NOT NULL DEFAULT '',
    max_sessions_week INTEGER,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS availability_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tutor_id INTEGER NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    tutor_id INTEGER NOT NULL REFERENCES tutors(id),
    subject TEXT NOT NULL DEFAULT '',
    session_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    length_minutes INTEGER NOT NULL DEFAULT 60
        CHECK (length_minutes IN (60, 90)),
    status TEXT NOT NULL DEFAULT 'booked'
        CHECK (status IN ('booked', 'attended', 'cancelled', 'missed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_sessions_tutor ON sessions(tutor_id);
CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_windows_tutor ON availability_windows(tutor_id);
"""


def get_db():
    if "db" not in g:
        path = current_app.config["DATABASE"]
        if path != ":memory:":
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
