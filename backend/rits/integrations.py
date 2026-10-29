"""Typed contract for cross-application adapters.

Adapters must declare their capabilities before they can be offered to the
assistant. This module deliberately provides no generic shell or UI executor.
"""
from dataclasses import dataclass
from typing import Protocol, Any, Literal


DataClass = Literal["local-only", "sends-to-provider", "reads-private-data", "modifies-external-state"]


@dataclass(frozen=True)
class Capability:
    capability_id: str
    description: str
    data_class: DataClass
    requires_confirmation: bool


@dataclass(frozen=True)
class AdapterInfo:
    adapter_id: str
    display_name: str
    description: str
    capabilities: tuple[Capability, ...]
    enabled: bool = False


class IntegrationAdapter(Protocol):
    """An app integration must implement this narrow, inspectable interface."""

    @property
    def info(self) -> AdapterInfo: ...

    def health_check(self) -> bool: ...

    def execute(self, capability_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one declared capability after the permission gate approves it."""
        ...


def list_adapter_info(adapters: list[IntegrationAdapter]) -> list[dict[str, Any]]:
    """Return safe metadata; never return credentials or arbitrary runtime objects."""
    return [
        {
            "adapter_id": adapter.info.adapter_id,
            "display_name": adapter.info.display_name,
            "description": adapter.info.description,
            "enabled": adapter.info.enabled,
            "health": "available" if adapter.health_check() else "unavailable",
            "capabilities": [
                {
                    "capability_id": capability.capability_id,
                    "description": capability.description,
                    "data_class": capability.data_class,
                    "requires_confirmation": capability.requires_confirmation,
                }
                for capability in adapter.info.capabilities
            ],
        }
        for adapter in adapters
    ]
