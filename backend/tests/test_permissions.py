import pytest
from rits.permissions import ConfirmationGate
from rits.registry import Action, ActionRegistry


def make_registry(calls):
    registry = ActionRegistry()
    registry.register(Action(
        action_id="test.external-change",
        description="Test-only simulated external change",
        handler=lambda args: calls.append(args.get("value")) or "simulated",
        requires_confirmation=True,
    ))
    return registry


def test_consequential_action_requires_ticket():
    calls = []
    registry = make_registry(calls)
    with pytest.raises(PermissionError):
        registry.execute("test.external-change", {"value": "no"})
    assert calls == []


def test_confirmation_ticket_executes_once():
    calls = []
    registry = make_registry(calls)
    gate = ConfirmationGate()
    pending = gate.request(registry, "test.external-change", {"value": "yes"})
    assert gate.confirm(registry, pending.token) == "simulated"
    assert calls == ["yes"]
    with pytest.raises(PermissionError):
        gate.confirm(registry, pending.token)
    assert calls == ["yes"]


def test_cannot_request_ticket_for_safe_action():
    calls = []
    registry = make_registry(calls)
    registry.register(Action("test.safe", "Safe test", lambda _: "ok"))
    with pytest.raises(ValueError):
        ConfirmationGate().request(registry, "test.safe")
