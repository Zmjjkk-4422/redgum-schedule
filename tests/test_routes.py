"""Smoke and form-post tests for the delivered web routes (RED-04/05/06)."""
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


def test_create_tutor_and_window_via_forms(client, ctx):
    response = client.post(
        "/tutors/new",
        data={"name": "Tomas Ferreira", "subjects": "Physics", "max_sessions_week": "8"},
    )
    assert response.status_code == 302
    from app import models
    tutor = models.list_tutors()[0]
    response = client.post(
        f"/tutors/{tutor['id']}/availability",
        data={"weekday": "2", "start_time": "15:30", "end_time": "19:00", "note": ""},
    )
    assert response.status_code == 302
    assert len(models.list_windows(tutor["id"])) == 1


def test_deactivate_tutor_via_form(client, ctx):
    client.post("/tutors/new", data={"name": "Temp Tutor", "subjects": "Maths"})
    from app import models
    tutor = models.list_tutors()[0]
    client.post(f"/tutors/{tutor['id']}/deactivate")
    assert models.get_tutor(tutor["id"])["status"] == "inactive"
