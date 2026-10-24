from fastapi.testclient import TestClient
from app import app, detect_red_flags

client=TestClient(app)

def test_health_endpoint():
    r=client.get("/api/health")
    assert r.status_code==200 and r.json()["ok"] is True

def test_emergency_bypasses_model_and_matching():
    r=client.post("/api/agent",json={"message":"I have severe chest pain and cannot breathe"}).json()
    assert r["status"]=="emergency_review"
    assert r["caregivers"]==[]
    assert r["urgency_prediction"] is None
    assert r["safety_flags"]

def test_short_intake_asks_followup():
    r=client.post("/api/agent",json={"message":"need help"}).json()
    assert r["status"]=="needs_follow_up"
    assert r["follow_up_question"]

def test_normal_intake_requires_human_review():
    r=client.post("/api/agent",json={"message":"I have had a headache for two days and need advice"}).json()
    assert r["needs_human_review"] is True
    assert r["status"]=="decision_support"

def test_hindi_red_flag():
    assert "possible_chest_pain" in detect_red_flags("मुझे सीने में दर्द हो रहा है")
