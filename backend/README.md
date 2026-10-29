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
- `GET /api/integrations` lists enabled app adapters (currently an empty list).\n- `GET /api/provider` reports whether Gemini is configured without exposing the API key.
- `POST /api/command` routes deterministic local commands.
- `POST /api/confirmations` creates a short-lived, one-use approval ticket for an allowlisted confirmation-required action.
- `POST /api/confirmations/{token}/approve` consumes a ticket and executes its registered action.
- `DELETE /api/confirmations/{token}` rejects and invalidates a pending ticket.

Try `help`, `status`, `draft your text`, or `demo approval`. The demo approval command shows the explicit review/approve/reject UI; its handler has no external side effects. Drafting creates a preview proposal only; it never sends a message.

## Integration and permission contracts

- `rits.integrations` defines typed adapter/capability metadata and health checks.
- Adapters must declare their data behavior and whether a capability requires confirmation.
- `rits.permissions.ConfirmationGate` issues short-lived, one-use, in-memory tickets for registered actions requiring confirmation.
- `ActionRegistry.execute` refuses confirmed-only actions; those can only use the separate confirmation path.
- No adapter is enabled by default and there is no generic shell executor.

The confirmation gate is connected to the UI approval dialog. Tickets expire after 120 seconds and can be used once. The only confirmation-required action registered in this foundation is a harmless demo handler. Do not register real external-state-changing actions until adapter-specific argument validation, threat modeling, and integration tests are implemented.

Gemini text replies are optional and are enabled only when `RITS_GEMINI_API_KEY` is set in the environment before RITS starts. Set `RITS_GEMINI_MODEL` optionally; the default is `gemini-3.8-flash`. Gemini is used only after local rules fail and receives no tools or action executor. The key is never stored in the repository or returned by the API. TTS, microphone, wake-word detection, and external-app integration are not enabled yet.
