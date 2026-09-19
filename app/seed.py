"""Seed-data command: loads the fictional case-study sample data.

Usage:  flask --app wsgi seed
"""
import json
import os

import click

from . import models
from .db import get_db


def register_commands(app):
    @app.cli.command("seed")
    def seed_command():
        """Load sample data from app/seed_data.json (idempotent by name)."""
        path = os.path.join(os.path.dirname(__file__), "seed_data.json")
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)

        db = get_db()
        tutor_ids = {}
        for tutor_data in data["tutors"]:
            existing = db.execute(
                "SELECT id FROM tutors WHERE name=?", (tutor_data["name"],)
            ).fetchone()
            if existing:
                tutor_id = existing["id"]
            else:
                cur = db.execute(
                    "INSERT INTO tutors (name, subjects, max_sessions_week) VALUES (?, ?, ?)",
                    (
                        tutor_data["name"],
                        tutor_data["subjects"],
                        tutor_data.get("max_sessions_week"),
                    ),
                )
                tutor_id = cur.lastrowid
            tutor_ids[tutor_data["name"]] = tutor_id
            for window in tutor_data.get("windows", []):
                dup = db.execute(
                    "SELECT id FROM availability_windows WHERE tutor_id=? AND weekday=? "
                    "AND start_time=? AND end_time=?",
                    (
                        tutor_id,
                        window["weekday"],
                        window["start_time"],
                        window["end_time"],
                    ),
                ).fetchone()
                if dup is None:
                    db.execute(
                        "INSERT INTO availability_windows "
                        "(tutor_id, weekday, start_time, end_time, note) VALUES (?, ?, ?, ?, ?)",
                        (
                            tutor_id,
                            window["weekday"],
                            window["start_time"],
                            window["end_time"],
                            window.get("note", ""),
                        ),
                    )

        student_ids = {}
        for student_data in data["students"]:
            existing = db.execute(
                "SELECT id FROM students WHERE name=?", (student_data["name"],)
            ).fetchone()
            if existing:
                student_ids[student_data["name"]] = existing["id"]
                continue
            # Diary-derived sample students predate the new contact-data
            # standard and intentionally have no family contact on record;
            # they are inserted directly rather than through UI validation.
            cur = db.execute(
                "INSERT INTO students (name, year_level, contact_name, contact_phone, "
                "contact_email, subjects) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    student_data["name"],
                    student_data["year_level"],
                    student_data.get("contact_name", ""),
                    student_data.get("contact_phone", ""),
                    student_data.get("contact_email", ""),
                    student_data.get("subjects", ""),
                ),
            )
            student_ids[student_data["name"]] = cur.lastrowid

        for session_data in data.get("sessions", []):
            student_id = student_ids.get(session_data["student"])
            tutor_id = tutor_ids.get(session_data["tutor"])
            if not student_id or not tutor_id:
                continue
            dup = db.execute(
                "SELECT id FROM sessions WHERE student_id=? AND tutor_id=? AND session_date=? "
                "AND start_time=?",
                (
                    student_id,
                    tutor_id,
                    session_data["session_date"],
                    session_data["start_time"],
                ),
            ).fetchone()
            if dup:
                continue
            models.insert_session(
                {
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "subject": session_data["subject"],
                    "session_date": session_data["session_date"],
                    "start_time": session_data["start_time"],
                    "length_minutes": session_data["length_minutes"],
                },
                status=session_data["status"],
            )

        click.echo(
            f"Seed complete: {len(data['tutors'])} tutors, {len(data['students'])} students, "
            f"{len(data.get('sessions', []))} sample sessions."
        )
