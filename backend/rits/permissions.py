"""Short-lived, one-time confirmation tickets for consequential actions."""
from dataclasses import dataclass
from secrets import token_urlsafe
from time import monotonic
from typing import Any
from .registry import ActionRegistry


@dataclass(frozen=True)
class PendingConfirmation:
    token: str
    action_id: str
    arguments: dict[str, Any]
    description: str
    expires_at: float


class ConfirmationGate:
    """In-memory confirmation tickets; restart invalidates all pending tickets."""

    def __init__(self, ttl_seconds: int = 120) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        self._ttl_seconds = ttl_seconds
        self._pending: dict[str, PendingConfirmation] = {}

    def request(self, registry: ActionRegistry, action_id: str, arguments: dict[str, Any] | None = None) -> PendingConfirmation:
        proposal = registry.propose(action_id, arguments)
        if not proposal["requires_confirmation"]:
            raise ValueError("This action does not require a confirmation ticket.")
        token = token_urlsafe(32)
        pending = PendingConfirmation(
            token=token,
            action_id=action_id,
            arguments=proposal["arguments"],
            description=proposal["description"],
            expires_at=monotonic() + self._ttl_seconds,
        )
        self._pending[token] = pending
        return pending

    def reject(self, token: str) -> None:
        pending = self._pending.pop(token, None)
        if pending is None or monotonic() >= pending.expires_at:
            raise PermissionError("Confirmation is invalid, expired, or already used.")

    def confirm(self, registry: ActionRegistry, token: str) -> str:
        pending = self._pending.pop(token, None)
        if pending is None:
            raise PermissionError("Confirmation is invalid, expired, or already used.")
        if monotonic() >= pending.expires_at:
            raise PermissionError("Confirmation expired. Review the action and request a new confirmation.")
        # Only this separate path can execute registered confirmation-required actions.
        return registry.execute_confirmed(pending.action_id, pending.arguments)
