# Run the RITS foundation on Windows

This first implementation is a development foundation: a React UI and a local FastAPI command service. It is **not yet a packaged Tauri installer** and does not yet include Gemini, wake-word detection, speech recognition, TTS, or third-party app control.

## Requirements

- Windows 10/11
- Python 3.11+
- Node.js 20+ and npm

## 1. Start the local backend

Open PowerShell in the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[dev]"
python -m uvicorn rits.app:app --app-dir backend --host 127.0.0.1 --port 8765
```

The service listens on loopback only at `http://127.0.0.1:8765`. Check `http://127.0.0.1:8765/health`.

## 2. Start the UI

Open a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local address Vite prints (normally `http://127.0.0.1:5173`).

## 3. Try local commands

- `help` — shows available commands
- `status` — checks the local core
- `draft I will be there in ten minutes` — creates a preview proposal; it does not send a message

## 4. Run backend tests

From the repository root, with the virtual environment active:

```powershell
python -m pytest backend/tests
```

## Safety boundaries in this build

- No arbitrary shell command endpoint.
- The API binds to `127.0.0.1`, not the whole network.
- Local commands do not call a cloud AI provider.
- Drafts are previews, never sent automatically.
- Real integrations must be registered behind capability and permission checks before they can perform actions.

## Current limitations

The UI and API have been added to the repository, but this environment has not executed Windows builds or tests. Treat the first local run as a validation step. The next implementation stage is packaging the UI as a Tauri desktop app and adding typed integration/permission interfaces before connecting AI providers.
