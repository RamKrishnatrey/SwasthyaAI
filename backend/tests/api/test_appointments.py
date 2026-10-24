from conftest import call, register_and_login


def test_appointment_request_stays_requested_and_is_patient_owned(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "appointment-1"}
    request = {"care_type": "teleconsultation", "requested_for": "2026-11-01T10:00:00Z"}

    created = call(app, "POST", "/api/v1/appointments", headers=headers, json=request)
    listed = call(app, "GET", "/api/v1/appointments", headers=headers)

    assert created.status_code == 201
    assert created.json()["status"] == "requested"
    assert listed.json()[0]["appointment_id"] == created.json()["appointment_id"]
    assert "confirmed" not in created.json()["status"]


def test_replayed_appointment_request_returns_the_existing_requested_item(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "request-123"}
    payload = {"care_type": "teleconsultation"}

    first = call(app, "POST", "/api/v1/appointments", headers=headers, json=payload)
    replay = call(app, "POST", "/api/v1/appointments", headers=headers, json=payload)

    assert first.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["appointment_id"] == first.json()["appointment_id"]
    assert replay.json()["status"] == "requested"


def test_reused_idempotency_key_with_different_request_is_rejected(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "request-456"}
    first = call(app, "POST", "/api/v1/appointments", headers=headers, json={"care_type": "teleconsultation"})
    changed = call(app, "POST", "/api/v1/appointments", headers=headers, json={"care_type": "home_nursing"})

    assert first.status_code == 201
    assert changed.status_code == 409


def test_clinician_cannot_create_patient_appointment(app):
    token = register_and_login(app, role="clinician")

    response = call(app, "POST", "/api/v1/appointments", headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "clinician-request"}, json={"care_type": "teleconsultation"})

    assert response.status_code == 403
