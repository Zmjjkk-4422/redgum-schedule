"""Smoke and form-post tests for the delivered web routes (RED-04/05)."""
def test_pages_load(client):
    for path in ("/", "/students/", "/tutors/", "/sessions/", "/schedule/"):
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


def test_create_tutor_via_form(client, ctx):
    response = client.post(
        "/tutors/new",
        data={"name": "Tomas Ferreira", "subjects": "Physics", "max_sessions_week": "8"},
    )
    assert response.status_code == 302
    from app import models
    assert any(t["name"] == "Tomas Ferreira" for t in models.list_tutors())


def test_deactivate_tutor_via_form(client, ctx):
    client.post("/tutors/new", data={"name": "Temp Tutor", "subjects": "Maths"})
    from app import models
    tutor = models.list_tutors()[0]
    client.post(f"/tutors/{tutor['id']}/deactivate")
    assert models.get_tutor(tutor["id"])["status"] == "inactive"
