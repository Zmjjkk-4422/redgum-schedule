"""Schedule view routes (Jira RED-09/10, owner: Jiao).

Delivered on feature/RED-09-schedule-views and
feature/RED-10-tutor-student-views during Sprint Weeks 2-3.
"""
from flask import Blueprint, render_template

bp = Blueprint("schedule", __name__, url_prefix="/schedule")

ACCEPTANCE_CRITERIA = [
    ("RED-09 Centre day/week schedule", [
        "Choose a day or a week and see every session with student, tutor, subject, time, length and status.",
        "Days with no sessions show an empty state, never an error.",
        "The view is usable on a phone-width browser without horizontal scrolling.",
    ]),
    ("RED-10 Tutor and student views", [
        "A tutor sees only their own upcoming sessions, soonest first; none shows an empty state.",
        "A student record shows past and future sessions in date order.",
        "Cancelled sessions remain visible and are clearly marked.",
    ]),
]


@bp.route("/")
def index():
    return render_template(
        "coming_soon.html",
        title="Schedule views",
        jira_ids="RED-09 / RED-10",
        owner="Jiao (Member C)",
        criteria=ACCEPTANCE_CRITERIA,
    )
