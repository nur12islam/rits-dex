# RITS backend

Local-first command API for the RITS desktop assistant foundation.

## Run on Windows

From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .\backend[dev]
python -m uvicorn rits.app:app --app-dir backend --host 127.0.0.1 --port 8765
```

The API binds only to loopback. Check `http://127.0.0.1:8765/health`.

## Current behavior

- `GET /health` reports local service health.
- `GET /api/actions` lists registered, allowlisted actions.
- `POST /api/command` routes deterministic local commands.
- Try `help`, `status`, or `draft your text`.
- Drafting creates a preview proposal only; it never sends a message.

No Gemini, TTS, microphone, shell execution, or external-app integration is enabled yet. Those should be added behind explicit provider and permission interfaces.
