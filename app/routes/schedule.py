"""Schedule view routes (Jira RED-09/10, owner: Jiao).

RED-09: centre day/week schedule view, mobile-friendly.
RED-10: tutor upcoming / student history views (later branch).
"""
from datetime import date, timedelta

from flask import Blueprint, render_template, request

from app import models

bp = Blueprint("schedule", __name__, url_prefix="/schedule")


def _parse_date(value):
    """Parse YYYY-MM-DD; fall back to today on anything malformed."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return date.today()


def _monday_of(day):
    """Return the Monday on or before the given date."""
    return day - timedelta(days=day.isoweekday() - 1)


@bp.route("/")
def index():
    view = request.args.get("view", "day")
    if view not in ("day", "week"):
        view = "day"
    day = _parse_date(request.args.get("date"))

    if view == "day":
        sessions = models.list_sessions(date=day.isoformat())
        period_label = day.strftime("%A, %d %B %Y")
        prev_date = day - timedelta(days=1)
        next_date = day + timedelta(days=1)
    else:
        start = _monday_of(day)
        end = start + timedelta(days=6)
        sessions = models.list_sessions(date=(start.isoformat(), end.isoformat()))
        period_label = f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"
        prev_date = start - timedelta(days=7)
        next_date = start + timedelta(days=7)

    return render_template(
        "schedule/index.html",
        title="Centre schedule",
        view=view,
        day=day,
        period_label=period_label,
        sessions=sessions,
        prev_date=prev_date.isoformat(),
        next_date=next_date.isoformat(),
    )


@bp.route("/tutor/<int:tutor_id>")
def tutor(tutor_id):
    """RED-10: a tutor sees only their own upcoming sessions, soonest first."""
    tutor = models.get_tutor(tutor_id)
    if tutor is None:
        return render_template("coming_soon.html", title="Tutor not found",
                               jira_ids="RED-10", owner="Jiao (Member C)", criteria=[]), 404
    today = date.today().isoformat()
    upcoming = [
        s for s in models.list_sessions(tutor_id=tutor_id)
        if s["session_date"] >= today
    ]
    return render_template(
        "schedule/tutor.html",
        title=f"{tutor['name']} — upcoming",
        tutor=tutor,
        sessions=upcoming,
    )
