"""Session booking routes (Jira RED-07/08, owner: Max).

The scheduling service already enforces the availability rule; these routes
provide the front-desk booking form, the session list, and the move/cancel
and status-transition flows.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import models
from ..services.availability import AvailabilityError
from ..services.scheduling import (
    SchedulingError,
    cancel_session,
    create_session,
    mark_session_status,
    move_session,
)

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


def _load_or_redirect(session_id):
    """Return (session, None) or (None, redirect response) for a missing id."""
    session = models.get_session(session_id)
    if session is None:
        flash("That session does not exist.", "danger")
        return None, redirect(url_for("sessions.index"))
    return session, None


@bp.route("/<int:session_id>/move", methods=("GET", "POST"))
def move(session_id):
    """Move a booked session to another slot; availability is re-checked."""
    session, err = _load_or_redirect(session_id)
    if err:
        return err

    if request.method == "POST":
        data = request.form.to_dict()
        try:
            moved = move_session(
                session_id,
                data.get("session_date"),
                data.get("start_time"),
                data.get("length_minutes") or None,
            )
        except (SchedulingError, AvailabilityError) as exc:
            flash(str(exc), "danger")
            return render_template("sessions/move.html", session=session, data=data)
        flash(
            f"Session moved: {moved['student_name']} with {moved['tutor_name']} "
            f"is now on {moved['session_date']} at {moved['start_time']} "
            f"({moved['length_minutes']} min).",
            "success",
        )
        return redirect(url_for("sessions.index", date=moved["session_date"]))

    return render_template(
        "sessions/move.html",
        session=session,
        data={
            "session_date": session["session_date"],
            "start_time": session["start_time"],
            "length_minutes": str(session["length_minutes"]),
        },
    )


@bp.route("/<int:session_id>/cancel", methods=("POST",))
def cancel(session_id):
    """Cancel a session; the record is retained and stays visible."""
    try:
        cancelled = cancel_session(session_id)
    except SchedulingError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("sessions.index"))
    flash(
        f"Session cancelled: {cancelled['student_name']} with "
        f"{cancelled['tutor_name']} on {cancelled['session_date']} at "
        f"{cancelled['start_time']}.",
        "success",
    )
    return redirect(url_for("sessions.index", date=cancelled["session_date"]))


@bp.route("/<int:session_id>/status", methods=("POST",))
def status(session_id):
    """Mark a booked session attended or missed (cancelled stays cancelled)."""
    new_status = request.form.get("status")
    try:
        updated = mark_session_status(session_id, new_status)
    except SchedulingError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("sessions.index"))
    flash(
        f"{updated['student_name']}'s session on {updated['session_date']} at "
        f"{updated['start_time']} marked {updated['status']}.",
        "success",
    )
    return redirect(url_for("sessions.index", date=updated["session_date"]))
