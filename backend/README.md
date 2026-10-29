# RITS backend

Local-first command API for the RITS desktop assistant foundation.

## Run on Windows

From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
Set-Location backend
python -m pip install -e ".[dev]"
Set-Location ..
python -m uvicorn rits.app:app --app-dir backend --host 127.0.0.1 --port 8765
```

The API binds to loopback only. Check `http://127.0.0.1:8765/health`.

## Endpoints

- `GET /health` reports local service health.
- `GET /api/actions` lists registered, allowlisted actions.
- `GET /api/integrations` lists enabled app adapters (currently an empty list).
- `POST /api/command` routes deterministic local commands.

Try `help`, `status`, or `draft your text`. Drafting creates a preview proposal only; it never sends a message.

## Integration and permission contracts

- `rits.integrations` defines typed adapter/capability metadata and health checks.
- Adapters must declare their data behavior and whether a capability requires confirmation.
- `rits.permissions.ConfirmationGate` issues short-lived, one-use, in-memory tickets for registered actions requiring confirmation.
- `ActionRegistry.execute` refuses confirmed-only actions; those can only use the separate confirmation path.
- No adapter is enabled by default and there is no generic shell executor.

The confirmation gate is currently a backend foundation, not yet connected to a user-facing approval dialog. Do not register real external-state-changing actions until the UI confirmation flow and adapter-specific argument validation are implemented and tested.

No Gemini, TTS, microphone, or external-app integration is enabled yet.
