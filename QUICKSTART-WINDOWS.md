# Run the RITS foundation on Windows

RITS now has a Tauri 2 desktop shell, a React/TypeScript UI, and a local FastAPI command service. The backend still runs as a separate process; it is **not bundled as a sidecar yet**. Gemini, wake-word detection, speech recognition, TTS, and third-party app control are not connected yet.

## Requirements

- Windows 10/11
- Python 3.11+
- Node.js 20+ and npm
- For the native desktop shell: Rust stable, Microsoft C++ Build Tools (MSVC), and WebView2 Runtime

## 1. Prepare the local backend

Open PowerShell in the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
Set-Location backend
python -m pip install -e ".[dev]"
Set-Location ..
python -m uvicorn rits.app:app --app-dir backend --host 127.0.0.1 --port 8765
```

Keep this terminal open. The service listens only on loopback at `http://127.0.0.1:8765`. Check `http://127.0.0.1:8765/health`.

## 2. Run the UI in a browser

Open a second PowerShell terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the local address Vite prints (normally `http://127.0.0.1:5173`).

## 3. Run the native desktop shell

After installing Rust and the Windows build prerequisites, open another terminal:

```powershell
Set-Location frontend
npm install
npm run tauri:dev
```

To build a Windows NSIS installer:

```powershell
npm run tauri:build
```

The desktop shell currently expects the backend to be started separately using step 1.

## 4. Try local commands

- `help` — shows available commands
- `status` — checks the local core
- `draft I will be there in ten minutes` — creates a preview proposal; it does not send a message

## 5. Run backend tests

From the repository root, with the virtual environment active:

```powershell
python -m pytest backend/tests
```

## Safety boundaries

- No arbitrary shell command endpoint.
- The API binds to `127.0.0.1`, not the whole network.
- Local commands do not call a cloud AI provider.
- Drafts are previews, never sent automatically.
- The UI uses system fonts and does not request Google Fonts.
- Real integrations must be registered behind capability and permission checks before they can perform actions.

## Validation status

The source files have been committed, but this environment has not executed Windows builds or tests. Please validate the first local run. Next, package the Python backend as a managed sidecar, then add typed integration/permission interfaces before connecting AI providers.
