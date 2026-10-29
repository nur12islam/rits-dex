import json
from io import BytesIO
import socket
from urllib.error import URLError

import pytest

from rits import gemini
from rits.gemini import GeminiUnavailable, generate_reply, provider_status


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_provider_status_never_returns_the_key(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-secret")
    status = provider_status()
    assert status["configured"] is True
    assert status["provider"] == "Gemini"
    assert "test-secret" not in repr(status)


def test_missing_key_is_reported_without_network(monkeypatch):
    monkeypatch.delenv("RITS_GEMINI_API_KEY", raising=False)
    with pytest.raises(GeminiUnavailable, match="not configured"):
        generate_reply("hello")


def test_generate_reply_parses_plain_text_and_uses_key_header(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-secret")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse({"candidates": [{"content": {"parts": [{"text": "Hello from RITS."}]}}]})

    monkeypatch.setattr(gemini, "urlopen", fake_urlopen)
    assert generate_reply("hello") == "Hello from RITS."
    assert captured["url"].endswith("/gemini-3.8-flash:generateContent")
    assert captured["headers"]["X-goog-api-key"] == "test-secret"
    assert captured["timeout"] == 20.0
    assert "tools" not in captured["body"]


def test_empty_provider_answer_fails_closed(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(gemini, "urlopen", lambda *_args, **_kwargs: FakeResponse({"candidates": []}))
    with pytest.raises(GeminiUnavailable, match="no answer"):
        generate_reply("hello")



def test_network_errors_explain_dns_failure_without_leaking_secrets(monkeypatch):
    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-secret")

    def fail_dns(*_args, **_kwargs):
        raise URLError(socket.gaierror("private diagnostic detail"))

    monkeypatch.setattr(gemini, "urlopen", fail_dns)
    with pytest.raises(GeminiUnavailable, match="DNS lookup failed") as error:
        generate_reply("hello")
    assert "test-secret" not in str(error.value)
    assert "private diagnostic detail" not in str(error.value)


def test_network_errors_explain_tls_failure(monkeypatch):
    import ssl

    monkeypatch.setenv("RITS_GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        gemini,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError(ssl.SSLCertVerificationError("secret detail"))),
    )
    with pytest.raises(GeminiUnavailable, match="TLS verification failed"):
        generate_reply("hello")
