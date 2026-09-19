"""Session booking routes (Jira RED-07/08, owner: Max).

The scheduling service and availability rule already exist in
app/services; the web flows below are delivered on the
feature/RED-07-book-session and feature/RED-08-move-cancel branches
during Sprint Week 2. This placeholder keeps the app runnable and
documents the acceptance criteria the UI must satisfy.
"""
from flask import Blueprint, render_template

bp = Blueprint("sessions", __name__, url_prefix="/sessions")

ACCEPTANCE_CRITERIA = [
    ("RED-07 Book a session", [
        "Choose one active student, one active tutor, a date, a start time and a length of 60 or 90 minutes.",
        "The booking is saved with status 'booked' and appears on that day's schedule.",
        "Bookings outside the tutor's availability windows for that weekday are refused with a clear reason.",
        "Deactivated tutors cannot be selected for new bookings.",
        "Missing required fields are named and nothing is saved.",
    ]),
    ("RED-08 Move, cancel and update a session", [
        "A session can be moved to a new date/time; the availability rule is re-checked on the new slot.",
        "A session can be cancelled; the record stays visible with status 'cancelled'.",
        "Booked sessions can be marked attended or missed; cancelled sessions cannot.",
        "Moving or cancelling one session never changes any other session.",
    ]),
]


@bp.route("/")
def index():
    return render_template(
        "coming_soon.html",
        title="Sessions",
        jira_ids="RED-07 / RED-08",
        owner="Max (Member B)",
        criteria=ACCEPTANCE_CRITERIA,
    )
