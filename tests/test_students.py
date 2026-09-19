"""Tests for student record validation and persistence (RED-04)."""
from app import models


def test_create_student_persists(ctx):
    student, errors = models.create_student(
        {"name": "Kai Lombardo", "year_level": "11", "contact_name": "Gina",
         "contact_phone": "0418 330 297", "contact_email": "", "subjects": "Physics"}
    )
    assert errors == []
    fetched = models.get_student(student["id"])
    assert fetched["name"] == "Kai Lombardo"
    assert fetched["year_level"] == 11
    assert fetched["status"] == "active"


def test_student_requires_name(ctx):
    student, errors = models.create_student(
        {"name": "  ", "year_level": "11", "contact_phone": "0418 330 297"}
    )
    assert student is None
    assert any("name" in e for e in errors)


def test_student_requires_contact(ctx):
    student, errors = models.create_student(
        {"name": "No Contact Kid", "year_level": "9", "contact_phone": "", "contact_email": ""}
    )
    assert student is None
    assert any("contact" in e for e in errors)


def test_student_year_level_range(ctx):
    student, errors = models.create_student(
        {"name": "Wrong Year", "year_level": "13", "contact_phone": "0400 000 000"}
    )
    assert student is None
    assert any("Year" in e for e in errors)


def test_email_alone_satisfies_contact(ctx):
    student, errors = models.create_student(
        {"name": "Email Only", "year_level": "7", "contact_email": "a@example.com"}
    )
    assert errors == [] and student is not None


def test_deactivate_hides_from_active_but_keeps_record(ctx):
    student, _ = models.create_student(
        {"name": "Leaving Student", "year_level": "10", "contact_phone": "0400 000 000"}
    )
    models.set_student_status(student["id"], "inactive")
    assert all(s["id"] != student["id"] for s in models.list_students(active_only=True))
    assert models.get_student(student["id"])["status"] == "inactive"


def test_update_student(ctx):
    student, _ = models.create_student(
        {"name": "Typo Name", "year_level": "10", "contact_phone": "0400 000 000"}
    )
    errors = models.update_student(
        student["id"],
        {"name": "Corrected Name", "year_level": "11", "contact_phone": "0400 000 001",
         "subjects": "Chemistry"},
    )
    assert errors == []
    fetched = models.get_student(student["id"])
    assert fetched["name"] == "Corrected Name"
    assert fetched["year_level"] == 11
