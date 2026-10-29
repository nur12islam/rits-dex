"""Deterministic command routing before any optional AI provider."""
from .models import CommandResponse
from .registry import ActionRegistry


def route_command(text: str, registry: ActionRegistry) -> CommandResponse:
    normalized = " ".join(text.strip().lower().split())
    if not normalized:
        return CommandResponse(source="not-understood", message="Type a command to get started.")

    if normalized in {"help", "commands", "what can you do"}:
        message = registry.execute("assistant.help")
        return CommandResponse(source="local-rule", message=message)

    if normalized in {"status", "system status", "rits status"}:
        message = registry.execute("assistant.status")
        return CommandResponse(source="local-rule", message=message)

    if normalized in {"demo approval", "test approval", "approval demo"}:
        return CommandResponse(
            source="local-rule",
            message="This is a simulated approval walkthrough. It has no external side effects.",
            proposal={
                "action_id": "demo.approval-check",
                "arguments": {"demo": True},
                "requires_confirmation": True,
                "description": "Run a local-only approval demonstration; no files, messages, or apps will be changed",
            },
        )

    if normalized.startswith("draft "):
        draft_text = text.strip()[6:].strip()
        if not draft_text:
            return CommandResponse(source="not-understood", message="Add the message you want me to draft.")
        return CommandResponse(
            source="local-rule",
            message="Draft prepared locally. Review it before copying or sending.",
            proposal={
                "action_id": "message.draft",
                "arguments": {"text": draft_text},
                "requires_confirmation": False,
                "description": "Prepare text for review; does not send anything",
            },
        )

    return CommandResponse(
        source="not-understood",
        message="I don't have a local rule for that yet. The Gemini provider and app adapters are not connected in this foundation build.",
    )
