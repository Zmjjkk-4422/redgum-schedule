"""Student record routes (Jira RED-04, owner: Han)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import models

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.route("/")
def index():
    return render_template("students/list.html", students=models.list_students())


@bp.route("/new", methods=("GET", "POST"))
def new():
    if request.method == "POST":
        data = request.form.to_dict()
        student, errors = models.create_student(data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("students/form.html", student=None, data=data)
        flash(f"Student {student['name']} created.", "success")
        return redirect(url_for("students.detail", student_id=student["id"]))
    return render_template("students/form.html", student=None, data={})


@bp.route("/<int:student_id>")
def detail(student_id):
    student = models.get_student(student_id)
    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("students.index"))
    sessions = models.list_sessions(student_id=student_id)
    return render_template("students/detail.html", student=student, sessions=sessions)


@bp.route("/<int:student_id>/edit", methods=("GET", "POST"))
def edit(student_id):
    student = models.get_student(student_id)
    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("students.index"))
    if request.method == "POST":
        errors = models.update_student(student_id, request.form.to_dict())
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "students/form.html", student=student, data=request.form.to_dict()
            )
        flash("Student updated.", "success")
        return redirect(url_for("students.detail", student_id=student_id))
    return render_template("students/form.html", student=student, data=student)


@bp.post("/<int:student_id>/<any(deactivate, activate):action>")
def set_status(student_id, action):
    models.set_student_status(student_id, "inactive" if action == "deactivate" else "active")
    flash(f"Student {action}d.", "warning" if action == "deactivate" else "success")
    return redirect(request.referrer or url_for("students.index"))
