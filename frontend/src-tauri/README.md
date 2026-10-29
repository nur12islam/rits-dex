# Tauri desktop shell

This folder contains the Tauri 2 desktop wrapper for the React UI. The desktop shell manages the local backend process: it starts it on launch, waits briefly for the local port, and stops the child process when RITS exits.

## Windows build prerequisites

- Windows 10/11
- Python 3.11+ (for development; the release backend is bundled)
- Node.js 20+
- Rust stable toolchain
- Microsoft C++ Build Tools (MSVC)
- WebView2 Runtime

## Development

Create and activate a Python virtual environment from the repository root, then install the backend and frontend dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[dev]"
Set-Location frontend
npm install
npm run tauri:dev
```

Keep the virtual environment activated when launching `tauri:dev`: the desktop shell starts `python -m uvicorn` itself. You no longer need a separate backend terminal. If Python or its backend dependencies cannot be found, the UI remains available and reports the core as offline.

## Windows release installer

From an activated Python environment, run:

```powershell
Set-Location frontend
npm install
npm run tauri:build
```

The Tauri build runs `backend/build_backend.py` on Windows, packages the API into `rits-backend.exe`, and bundles it as a resource. The generated executable is local build output and must not be committed. The installed desktop app starts that bundled executable and stops it on exit.

The service binds to `127.0.0.1:8765` only. Never package API keys in the desktop bundle. Gemini, speech, wake-word detection, TTS, and third-party app adapters are not enabled yet.
