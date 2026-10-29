"""Shared request and response models for the RITS API."""
from typing import Any, Literal
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ActionProposal(BaseModel):
    action_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    description: str


class CommandResponse(BaseModel):
    source: Literal["local-rule", "help", "not-understood"]
    message: str
    proposal: ActionProposal | None = None
