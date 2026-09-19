"""Shared pytest fixtures."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app import models  # noqa: E402


@pytest.fixture
def app(tmp_path):
    application = create_app("test", {"DATABASE": str(tmp_path / "test.db")})
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def tutor_with_windows(ctx):
    """Tomas with the Term 3 availability-card windows (no Friday)."""
    tutor, _ = models.create_tutor(
        {"name": "Tomas Ferreira", "subjects": "Physics, Chemistry, Math Methods",
         "max_sessions_week": "8"}
    )
    for weekday, start, end, note in [
        (2, "15:30", "19:00", ""),
        (3, "15:30", "18:00", ""),
        (4, "16:00", "18:30", "Amended 21 July"),
        (6, "09:00", "12:30", ""),
    ]:
        assert models.add_window(
            tutor["id"],
            {"weekday": str(weekday), "start_time": start, "end_time": end, "note": note},
        ) == []
    return tutor


@pytest.fixture
def active_student(ctx):
    student, _ = models.create_student(
        {"name": "Kai Lombardo", "year_level": "11", "contact_name": "Gina Lombardo",
         "contact_phone": "0418 330 297", "contact_email": "", "subjects": "Physics, Math Methods"}
    )
    return student
