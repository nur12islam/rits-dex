from rits.registry import build_default_registry
from rits.router import route_command


def test_help_is_local():
    result = route_command("help", build_default_registry())
    assert result.source == "local-rule"
    assert "Try:" in result.message


def test_status_does_not_require_ai():
    result = route_command("status", build_default_registry())
    assert result.source == "local-rule"
    assert "No cloud AI provider" in result.message


def test_draft_does_not_send_message():
    result = route_command("draft Tell them I will be late", build_default_registry())
    assert result.proposal is not None
    assert result.proposal.action_id == "message.draft"
    assert result.proposal.arguments["text"] == "Tell them I will be late"
    assert "does not send" in result.proposal.description


def test_unknown_command_is_honest_about_missing_provider():
    result = route_command("open my calendar", build_default_registry())
    assert result.source == "not-understood"
    assert "not connected" in result.message
