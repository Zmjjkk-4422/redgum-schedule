"""Tutor record routes (Jira RED-05, owner: Han).

Availability-window maintenance is delivered separately as RED-06.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import models

bp = Blueprint("tutors", __name__, url_prefix="/tutors")


@bp.route("/")
def index():
    return render_template("tutors/list.html", tutors=models.list_tutors())


@bp.route("/new", methods=("GET", "POST"))
def new():
    if request.method == "POST":
        data = request.form.to_dict()
        tutor, errors = models.create_tutor(data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("tutors/form.html", tutor=None, data=data)
        flash(f"Tutor {tutor['name']} created.", "success")
        return redirect(url_for("tutors.index"))
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
