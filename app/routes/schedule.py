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
