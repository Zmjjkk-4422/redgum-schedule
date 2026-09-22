"""Session booking routes (Jira RED-07, owner: Max).

The scheduling service already enforces the availability rule; these routes
provide the front-desk booking form and the session list.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import models
from ..services.scheduling import create_session

bp = Blueprint("sessions", __name__, url_prefix="/sessions")


@bp.route("/")
def index():
    date = request.args.get("date") or None
    sessions = models.list_sessions(date=date)
    return render_template("sessions/list.html", sessions=sessions, date=date)


@bp.route("/book", methods=("GET", "POST"))
def book():
    students = models.list_students(active_only=True)
    tutors = models.list_tutors(active_only=True)

    if request.method == "POST":
        data = request.form.to_dict()
        session, errors = create_session(data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "sessions/book.html",
                students=students, tutors=tutors, data=data,
            )
        flash(
            f"Session booked: {session['student_name']} with "
            f"{session['tutor_name']} on {session['session_date']} "
            f"at {session['start_time']} ({session['length_minutes']} min).",
            "success",
        )
        return redirect(url_for("sessions.index", date=session["session_date"]))

    return render_template(
        "sessions/book.html", students=students, tutors=tutors, data={}
    )
