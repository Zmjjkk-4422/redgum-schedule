"""Smoke and form-post tests for the student web routes (RED-04)."""
def test_pages_load(client):
    for path in ("/", "/students/", "/sessions/", "/schedule/"):
        response = client.get(path)
        assert response.status_code == 200, path


def test_create_student_via_form(client, ctx):
    response = client.post(
        "/students/new",
        data={"name": "Kai Lombardo", "year_level": "11", "contact_name": "Gina",
              "contact_phone": "0418 330 297", "contact_email": "", "subjects": "Physics"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    from app import models
    students = models.list_students()
    assert any(s["name"] == "Kai Lombardo" for s in students)


def test_student_form_validation_flashes(client):
    response = client.post(
        "/students/new",
        data={"name": "", "year_level": "", "contact_phone": "", "contact_email": ""},
    )
    assert response.status_code == 200
    assert b"required" in response.data


def test_deactivate_student_via_form(client, ctx):
    client.post(
        "/students/new",
        data={"name": "Leaving Student", "year_level": "10", "contact_phone": "0400 000 000"},
    )
    from app import models
    student = models.list_students()[0]
    client.post(f"/students/{student['id']}/deactivate")
    assert models.get_student(student["id"])["status"] == "inactive"
