"""RITS API entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import CommandRequest, CommandResponse, ConfirmationRequest, ConfirmationTicket, ConfirmationResult
from .permissions import ConfirmationGate
from .registry import Action, build_default_registry
from .router import route_command

app = FastAPI(title="RITS Local Core", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:5173", "http://127.0.0.1:5173", "http://tauri.localhost", "https://tauri.localhost", "tauri://localhost"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
registry = build_default_registry()
# A harmless local-only action makes the approval flow testable before real adapters exist.
registry.register(Action(
    action_id="demo.approval-check",
    description="Run a local-only approval demonstration; no files, messages, or apps will be changed",
    handler=lambda _: "Approval confirmed. This demo performed no external action.",
    requires_confirmation=True,
))
confirmation_gate = ConfirmationGate(ttl_seconds=120)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rits-local-core"}


@app.get("/api/actions")
def actions() -> list[dict[str, object]]:
    return registry.describe()


@app.get("/api/integrations")
def integrations() -> list[dict[str, object]]:
    """No third-party adapters are enabled in the foundation build."""
    return []


@app.post("/api/command", response_model=CommandResponse)
def command(request: CommandRequest) -> CommandResponse:
    return route_command(request.text, registry)


@app.post("/api/confirmations", response_model=ConfirmationTicket)
def request_confirmation(request: ConfirmationRequest) -> ConfirmationTicket:
    try:
        pending = confirmation_gate.request(registry, request.action_id, request.arguments)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Action is not registered.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ConfirmationTicket(
        token=pending.token,
        action_id=pending.action_id,
        arguments=pending.arguments,
        description=pending.description,
        expires_in_seconds=120,
    )


@app.post("/api/confirmations/{token}/approve", response_model=ConfirmationResult)
def approve_confirmation(token: str) -> ConfirmationResult:
    try:
        message = confirmation_gate.confirm(registry, token)
    except PermissionError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return ConfirmationResult(status="confirmed", message=message)


@app.delete("/api/confirmations/{token}", response_model=ConfirmationResult)
def reject_confirmation(token: str) -> ConfirmationResult:
    try:
        confirmation_gate.reject(token)
    except PermissionError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return ConfirmationResult(status="rejected", message="Action rejected. Nothing was executed.")
