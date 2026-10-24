from conftest import call, register_and_login


def test_registration_login_and_logout_revoke_session(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}"}

    assert call(app, "GET", "/api/v1/auth/me", headers=headers).json()["role"] == "patient"
    assert call(app, "POST", "/api/v1/auth/logout", headers=headers).status_code == 204
    assert call(app, "GET", "/api/v1/auth/me", headers=headers).status_code == 401


def test_invalid_password_and_duplicate_email_are_rejected(app):
    register_and_login(app)

    invalid = call(app, "POST", "/api/v1/auth/login", json={
        "email": "person@example.test", "password": "wrong password"
    })
    duplicate = call(app, "POST", "/api/v1/auth/register", json={
        "email": "person@example.test", "password": "another password", "role": "patient"
    })

    assert invalid.status_code == 401
    assert duplicate.status_code == 409


def test_expired_sessions_are_rejected(app):
    token = register_and_login(app)
    from backend.swasthyaai.services.auth import token_digest
    from backend.swasthyaai.config import get_settings
    import sqlite3

    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            "UPDATE sessions SET expires_at = '2000-01-01T00:00:00+00:00' WHERE token_digest = ?",
            (token_digest(token),),
        )

    assert call(app, "GET", "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_password_and_session_token_are_stored_only_as_hash_material(app):
    token = register_and_login(app)
    from backend.swasthyaai.config import get_settings
    import sqlite3

    with sqlite3.connect(get_settings().database_path) as connection:
        session_digest = connection.execute("SELECT token_digest FROM sessions").fetchone()[0]
        stored_password = connection.execute("SELECT password_hash FROM users").fetchone()[0]

    assert session_digest != token
    assert token not in session_digest
    assert b"correct horse battery staple" not in stored_password


def test_patient_token_cannot_access_clinician_endpoint(app):
    token = register_and_login(app)

    response = call(app, "GET", "/api/v1/clinician/records", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
