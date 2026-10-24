from conftest import call, register_and_login


def test_discovery_returns_empty_when_no_verified_caregiver_directory_exists(app):
    token = register_and_login(app)

    response = call(
        app,
        "GET",
        "/api/v1/caregivers?care_type=home_nursing&language=Hindi",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
