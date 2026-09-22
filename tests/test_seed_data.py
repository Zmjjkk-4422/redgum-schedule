"""Seed-data verification tests (Jira RED-11).

These prove that the single command ``flask --app wsgi seed`` loads the
case-study data the acceptance criteria name:

* Tomas Ferreira's card, including the max 8 sessions/week cap;
* his Term 3 Tuesday / Wednesday / Thursday / Saturday windows, with the
  Thursday window amended on 21 July (opens 16:00, not 15:00);
* Helen Vasquez enrolled with no availability windows;
* Kai Lombardo enrolled via his mother Gina;
* Jayden Pike's Thursday 18:30 session moved to Saturday 09:00 (Week 5 diary).
"""
import pytest

from app import models


@pytest.fixture
def seeded_ctx(app):
    """Run the seed CLI command against the test database, then yield a context."""
    result = app.test_cli_runner().invoke(args=["seed"])
    assert result.exit_code == 0, result.output
    with app.app_context():
        yield


def _tutor(name):
    return next(t for t in models.list_tutors() if t["name"] == name)


def _student(name):
    return next(s for s in models.list_students() if s["name"] == name)


def test_seed_loads_expected_counts(seeded_ctx):
    assert models.count_tutors() == 2
    assert models.count_students() == 6
    assert models.count_sessions() == 6


def test_tomas_card_has_eight_per_week_and_term3_windows(seeded_ctx):
    tomas = _tutor("Tomas Ferreira")
    assert tomas["max_sessions_week"] == 8

    windows = {w["weekday"]: w for w in models.list_windows(tomas["id"])}
    assert (windows[2]["start_time"], windows[2]["end_time"]) == ("15:30", "19:00")
    assert (windows[3]["start_time"], windows[3]["end_time"]) == ("15:30", "18:00")
    # Thursday window amended on 21 July: opens 16:00 (previously 15:00).
    assert (windows[4]["start_time"], windows[4]["end_time"]) == ("16:00", "18:30")
    assert "21 July" in windows[4]["note"]
    assert (windows[6]["start_time"], windows[6]["end_time"]) == ("09:00", "12:30")
    # No Friday window in Term 3.
    assert 5 not in windows


def test_helen_vasquez_enrolled_with_no_windows(seeded_ctx):
    helen = _tutor("Helen Vasquez")
    assert models.list_windows(helen["id"]) == []


def test_kai_lombardo_enrolled_via_mother(seeded_ctx):
    kai = _student("Kai Lombardo")
    assert "Gina" in kai["contact_name"]
    assert kai["contact_phone"].strip()


def test_jayden_pike_thursday_session_moved_to_saturday(seeded_ctx):
    jayden = _student("Jayden Pike")
    sessions = models.list_sessions(student_id=jayden["id"])
    moved_from = [
        s for s in sessions
        if s["session_date"] == "2026-08-13" and s["start_time"] == "18:30"
    ]
    moved_to = [
        s for s in sessions
        if s["session_date"] == "2026-08-15" and s["start_time"] == "09:00"
    ]
    assert moved_from[0]["status"] == "cancelled"
    assert moved_to[0]["status"] == "booked"


def test_seed_command_is_idempotent(app):
    runner = app.test_cli_runner()
    runner.invoke(args=["seed"])
    runner.invoke(args=["seed"])
    with app.app_context():
        assert models.count_tutors() == 2
        assert models.count_students() == 6
        assert models.count_sessions() == 6
