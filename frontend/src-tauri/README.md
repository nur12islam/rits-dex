# Tauri desktop shell

This folder contains the Tauri 2 desktop wrapper for the React UI.

## Windows build prerequisites

- Node.js 20+
- Rust stable toolchain
- Microsoft C++ Build Tools (MSVC)
- WebView2 Runtime

From the `frontend` directory:

```powershell
npm install
npm run tauri:dev
```

To create a Windows NSIS installer:

```powershell
npm run tauri:build
```

The FastAPI backend is currently a separate local process; it is not bundled as a sidecar yet. Start it using the root [Windows quickstart](../../QUICKSTART-WINDOWS.md) before testing commands in the UI. Never package API keys in the desktop bundle.
