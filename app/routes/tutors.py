"""Tutor record and availability-window routes (Jira RED-05/06, owner: Han)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import models

bp = Blueprint("tutors", __name__, url_prefix="/tutors")


@bp.route("/")
def index():
    tutors = models.list_tutors()
    windows = models.list_windows()
    by_tutor = {}
    for window in windows:
        by_tutor.setdefault(window["tutor_id"], []).append(window)
    return render_template(
        "tutors/list.html", tutors=tutors, windows_by_tutor=by_tutor
    )


@bp.route("/new", methods=("GET", "POST"))
def new():
    if request.method == "POST":
        data = request.form.to_dict()
        tutor, errors = models.create_tutor(data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("tutors/form.html", tutor=None, data=data)
        flash(f"Tutor {tutor['name']} created. Now add their availability windows.", "success")
        return redirect(url_for("tutors.availability", tutor_id=tutor["id"]))
    return render_template("tutors/form.html", tutor=None, data={})


@bp.route("/<int:tutor_id>/edit", methods=("GET", "POST"))
def edit(tutor_id):
    tutor = models.get_tutor(tutor_id)
    if tutor is None:
        flash("Tutor not found.", "danger")
        return redirect(url_for("tutors.index"))
    if request.method == "POST":
        errors = models.update_tutor(tutor_id, request.form.to_dict())
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "tutors/form.html", tutor=tutor, data=request.form.to_dict()
            )
        flash("Tutor updated.", "success")
        return redirect(url_for("tutors.index"))
    return render_template("tutors/form.html", tutor=tutor, data=tutor)


@bp.post("/<int:tutor_id>/<any(deactivate, activate):action>")
def set_status(tutor_id, action):
    models.set_tutor_status(tutor_id, "inactive" if action == "deactivate" else "active")
    flash(f"Tutor {action}d.", "warning" if action == "deactivate" else "success")
    return redirect(request.referrer or url_for("tutors.index"))


@bp.route("/<int:tutor_id>/availability", methods=("GET", "POST"))
def availability(tutor_id):
    tutor = models.get_tutor(tutor_id)
    if tutor is None:
        flash("Tutor not found.", "danger")
        return redirect(url_for("tutors.index"))
    if request.method == "POST":
        errors = models.add_window(tutor_id, request.form.to_dict())
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            flash("Availability window added.", "success")
        return redirect(url_for("tutors.availability", tutor_id=tutor_id))
    return render_template(
        "tutors/availability.html",
        tutor=tutor,
        windows=models.list_windows(tutor_id),
        weekday_names=models.WEEKDAY_NAMES,
    )


@bp.post("/windows/<int:window_id>/delete")
def delete_window(window_id):
    window = models.get_window(window_id)
    models.delete_window(window_id)
    flash("Availability window removed.", "warning")
    if window is not None:
        return redirect(url_for("tutors.availability", tutor_id=window["tutor_id"]))
    return redirect(url_for("tutors.index"))
