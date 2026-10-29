from fastapi.testclient import TestClient

from rits.app import app

client = TestClient(app)


def test_confirmation_demo_requires_explicit_approval():
    command = client.post("/api/command", json={"text": "demo approval"})
    assert command.status_code == 200
    proposal = command.json()["proposal"]
    assert proposal["requires_confirmation"] is True

    ticket_response = client.post("/api/confirmations", json={
        "action_id": proposal["action_id"],
        "arguments": proposal["arguments"],
    })
    assert ticket_response.status_code == 200
    ticket = ticket_response.json()
    assert ticket["action_id"] == "demo.approval-check"
    assert ticket["expires_in_seconds"] == 120

    approved = client.post(f"/api/confirmations/{ticket['token']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "confirmed"
    assert "no external action" in approved.json()["message"]

    replay = client.post(f"/api/confirmations/{ticket['token']}/approve")
    assert replay.status_code == 410


def test_rejecting_confirmation_does_not_execute_action():
    proposal = client.post("/api/command", json={"text": "demo approval"}).json()["proposal"]
    ticket = client.post("/api/confirmations", json={
        "action_id": proposal["action_id"],
        "arguments": proposal["arguments"],
    }).json()

    rejected = client.delete(f"/api/confirmations/{ticket['token']}")
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    replay = client.post(f"/api/confirmations/{ticket['token']}/approve")
    assert replay.status_code == 410


def test_cannot_request_confirmation_for_unregistered_action():
    response = client.post("/api/confirmations", json={
        "action_id": "system.execute-shell",
        "arguments": {"command": "whoami"},
    })
    assert response.status_code == 404
