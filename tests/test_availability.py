"""Tests for the tutor availability domain rule (RED-03).

The Definition of Done requires automated tests, including at least one test
of the availability rule. These cover valid boundary cases and every refusal
path, including moved sessions (tested in test_scheduling_service.py).
"""
import pytest

from app import models
from app.services.availability import AvailabilityError, validate_booking


def test_booking_inside_window_accepted(tutor_with_windows):
    # Tuesday 15:30-16:30 sits inside Tuesday 15:30-19:00.
    window = validate_booking(tutor_with_windows, 2, "16:00", 60)
    assert window["start_time"] == "15:30"


def test_booking_exactly_at_window_boundaries_accepted(tutor_with_windows):
    # Starts exactly when the window opens.
    assert validate_booking(tutor_with_windows, 2, "15:30", 60)
    # Ends exactly when the window closes (18:00 + 60 = 19:00).
    assert validate_booking(tutor_with_windows, 2, "18:00", 60)
    # 90-minute session ending exactly at Saturday close (11:00 + 90 = 12:30).
    assert validate_booking(tutor_with_windows, 6, "11:00", 90)


def test_booking_starting_before_window_refused(tutor_with_windows):
    # Thursday window opens 16:00 after the 21 July amendment.
    with pytest.raises(AvailabilityError) as exc:
        validate_booking(tutor_with_windows, 4, "15:30", 60)
    assert "before" in str(exc.value)


def test_booking_running_past_window_refused(tutor_with_windows):
    # 18:30 + 60 minutes runs past the Thursday 18:30 close.
    with pytest.raises(AvailabilityError) as exc:
        validate_booking(tutor_with_windows, 4, "18:00", 60)
    assert "runs past" in str(exc.value) or "past" in str(exc.value)


def test_booking_on_unavailable_day_refused(tutor_with_windows):
    # Tomas is never available on Fridays.
    with pytest.raises(AvailabilityError) as exc:
        validate_booking(tutor_with_windows, 5, "10:00", 60)
    assert "no availability window" in str(exc.value)


def test_booking_spanning_gap_between_two_windows_refused(ctx):
    tutor, _ = models.create_tutor({"name": "Split Day Tutor", "subjects": "Maths"})
    models.add_window(tutor["id"], {"weekday": 3, "start_time": "15:30", "end_time": "18:00"})
    models.add_window(tutor["id"], {"weekday": 3, "start_time": "19:00", "end_time": "20:00"})
    # 18:00-19:00 falls across the gap and inside neither window.
    with pytest.raises(AvailabilityError):
        validate_booking(tutor, 3, "18:00", 60)


def test_deactivated_tutor_booking_refused(tutor_with_windows):
    models.set_tutor_status(tutor_with_windows["id"], "inactive")
    tutor = models.get_tutor(tutor_with_windows["id"])
    with pytest.raises(AvailabilityError) as exc:
        validate_booking(tutor, 2, "16:00", 60)
    assert "deactivated" in str(exc.value)
