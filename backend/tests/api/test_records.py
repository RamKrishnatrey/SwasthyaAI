from conftest import call, register_and_login


def test_patient_can_create_and_read_records(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}"}
    created = call(app, "POST", "/api/v1/patient/records/allergies", headers=headers, json={"data": {"name": "Pollen"}})

    assert created.status_code == 201
    record_id = created.json()["record_id"]
    records = call(app, "GET", "/api/v1/patient/records/allergies", headers=headers)
    assert [item["record_id"] for item in records.json()] == [record_id]


def test_records_are_not_visible_to_another_patient_or_clinician(app):
    patient_token = register_and_login(app, email="patient@example.test")
    other_token = register_and_login(app, email="other@example.test")
    clinician_token = register_and_login(app, role="clinician", email="clinician@example.test")
    call(app, "POST", "/api/v1/patient/records/history", headers={"Authorization": f"Bearer {patient_token}"}, json={"data": {"summary": "Demo history"}})

    other_records = call(app, "GET", "/api/v1/patient/records/history", headers={"Authorization": f"Bearer {other_token}"})
    clinician_records = call(app, "GET", "/api/v1/patient/records/history", headers={"Authorization": f"Bearer {clinician_token}"})

    assert other_records.json() == []
    assert clinician_records.status_code == 403
