"""Allowlisted local actions. No arbitrary shell execution is exposed."""
from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class Action:
    action_id: str
    description: str
    handler: Callable[[dict[str, Any]], str]
    requires_confirmation: bool = False


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        if action.action_id in self._actions:
            raise ValueError(f"Action already registered: {action.action_id}")
        self._actions[action.action_id] = action

    def describe(self) -> list[dict[str, object]]:
        return [
            {
                "action_id": action.action_id,
                "description": action.description,
                "requires_confirmation": action.requires_confirmation,
            }
            for action in self._actions.values()
        ]

    def propose(self, action_id: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        action = self._actions.get(action_id)
        if action is None:
            raise KeyError(action_id)
        return {
            "action_id": action.action_id,
            "arguments": arguments or {},
            "requires_confirmation": action.requires_confirmation,
            "description": action.description,
        }

    def execute(self, action_id: str, arguments: dict[str, Any] | None = None) -> str:
        action = self._actions.get(action_id)
        if action is None:
            raise KeyError(action_id)
        if action.requires_confirmation:
            raise PermissionError("This action requires explicit user confirmation.")
        return action.handler(arguments or {})

    def execute_confirmed(self, action_id: str, arguments: dict[str, Any] | None = None) -> str:
        action = self._actions.get(action_id)
        if action is None:
            raise KeyError(action_id)
        if not action.requires_confirmation:
            raise ValueError("This action does not use the confirmation path.")
        return action.handler(arguments or {})


def build_default_registry() -> ActionRegistry:
    registry = ActionRegistry()
    registry.register(Action(
        action_id="assistant.help",
        description="Show available local-first RITS commands",
        handler=lambda _: "Try: help, status, or draft <text>. Actions that affect other apps will be added through permissioned adapters.",
    ))
    registry.register(Action(
        action_id="assistant.status",
        description="Show backend status",
        handler=lambda _: "RITS local core is running. No cloud AI provider is called by this action.",
    ))
    return registry
