from conftest import call, register_and_login


def test_reminder_is_created_as_an_in_app_demo_item(app):
    token = register_and_login(app)
    headers = {"Authorization": f"Bearer {token}"}
    created = call(app, "POST", "/api/v1/reminders", headers=headers, json={"text": "Bring your report"})

    assert created.status_code == 201
    assert created.json()["delivery"] == "in_app_demo"
    assert created.json()["status"] == "scheduled"
    assert call(app, "GET", "/api/v1/reminders", headers=headers).json()[0]["reminder_id"] == created.json()["reminder_id"]
