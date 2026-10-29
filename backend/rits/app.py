"""RITS API entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import CommandRequest, CommandResponse
from .registry import build_default_registry
from .router import route_command

app = FastAPI(title="RITS Local Core", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:5173", "tauri://localhost"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
registry = build_default_registry()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rits-local-core"}


@app.get("/api/actions")
def actions() -> list[dict[str, object]]:
    return registry.describe()


@app.post("/api/command", response_model=CommandResponse)
def command(request: CommandRequest) -> CommandResponse:
    return route_command(request.text, registry)
