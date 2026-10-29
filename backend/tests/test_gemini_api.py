from fastapi.testclient import TestClient

from rits import app as app_module

client = TestClient(app_module.app)


def test_provider_status_does_not_expose_secret(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "never-return-this")
    response = client.get("/api/provider")
    assert response.status_code == 200
    assert response.json()["configured"] is True
    assert "never-return-this" not in response.text


def test_local_commands_stay_local_when_gemini_is_configured(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-key")

    def should_not_call(_text):
        raise AssertionError("Gemini must not receive deterministic local commands")

    monkeypatch.setattr(app_module, "generate_reply", should_not_call)
    response = client.post("/api/command", json={"text": "help"})
    assert response.status_code == 200
    assert response.json()["source"] == "local-rule"


def test_unknown_prompt_uses_gemini_only_when_configured(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(app_module, "generate_reply", lambda text: f"AI reply: {text}")
    response = client.post("/api/command", json={"text": "Explain black holes"})
    assert response.status_code == 200
    assert response.json()["source"] == "ai"
    assert response.json()["message"] == "AI reply: Explain black holes"


def test_unknown_prompt_keeps_local_fallback_without_key(monkeypatch):
    monkeypatch.delenv("RITS_GEMINI_API_KEY", raising=False)
    response = client.post("/api/command", json={"text": "Explain black holes"})
    assert response.status_code == 200
    assert response.json()["source"] == "not-understood"
    assert "not connected" in response.json()["message"]
