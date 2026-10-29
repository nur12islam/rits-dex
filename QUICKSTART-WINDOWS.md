# Run RITS on Windows

RITS has a Tauri 2 desktop shell, a React/TypeScript UI, and a local FastAPI command service. In desktop development mode, the Tauri shell starts the local Python backend and terminates its child process when the app exits. For a Windows release build, the pre-build hook creates a self-contained backend executable and includes it in the installer.

Gemini, wake-word detection, speech recognition, TTS, and third-party app control are not connected yet.

## Requirements

- Windows 10/11
- Python 3.11+ and pip
- Node.js 20+ and npm
- For the native desktop shell: Rust stable, Microsoft C++ Build Tools (MSVC), and WebView2 Runtime

## 1. Install backend dependencies for development

Open PowerShell in the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]" --no-deps
```

If the editable install command above is run from the repository root, use the backend path instead:

```powershell
python -m pip install -e "./backend[dev]"
```

## 2. Run the desktop app (backend starts automatically)

```powershell
Set-Location frontend
npm install
npm run tauri:dev
```

The Tauri shell launches Python with Uvicorn bound to `127.0.0.1:8765`. It suppresses backend console output, waits briefly for the port, and kills the child process when RITS exits. The Python environment must already have the backend dependencies installed. If startup fails, the UI remains open and displays the core as offline; check the terminal output for the startup error.

## 3. Run the UI in a browser (manual backend)

If you only want to test the UI in a browser, start the backend in one PowerShell window:

```powershell
python -m uvicorn rits.app:app --app-dir backend --host 127.0.0.1 --port 8765
```

Then in another window:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the local address Vite prints. Stop the manually started backend yourself with Ctrl+C.

## 4. Build a Windows installer

On Windows, from the repository root with Python, Node, Rust and MSVC build tools installed:

```powershell
Set-Location frontend
npm install
npm run tauri:build
```

Tauri's pre-build hook runs the frontend build and `backend/build_backend.py`, which uses PyInstaller to create `rits-backend.exe` and copies it into Tauri's resource directory. The generated executable is a local build artifact and should not be committed. The installer build has not yet been validated on a Windows runner.

## 5. Try local commands

- `help` — shows available commands
- `status` — checks the local core
- `draft I will be there in ten minutes` — creates a preview proposal; it does not send a message

## Safety boundaries

- The backend binds to loopback only; it is not exposed to the local network.
- No arbitrary shell command endpoint is exposed.
- Local commands do not call a cloud AI provider.
- Drafts are previews, never sent automatically.
- The UI uses system fonts and does not request Google Fonts.
- Real integrations must be registered behind capability and permission checks before they can perform actions.
- The desktop shell terminates the backend process it starts. It does not kill unrelated processes.
- If another process already occupies port 8765, startup can fail; close that process before launching RITS.

## Validation status

GitHub Actions previously passed the backend tests and frontend build. The latest process-lifecycle and packaging changes require a fresh CI run, and a Windows/Tauri installer build still needs validation.
