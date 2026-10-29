# RITS desktop UI foundation

React + TypeScript + Vite interface with a Tauri 2 desktop wrapper.

## Browser development

Start the backend using [the Windows quickstart](../../QUICKSTART-WINDOWS.md). In a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Native desktop development

Install Rust stable, Microsoft C++ Build Tools (MSVC), and WebView2 Runtime, then:

```powershell
cd frontend
npm install
npm run tauri:dev
```

Build a Windows NSIS installer with `npm run tauri:build`.

The FastAPI backend still runs as a separate local process and is not bundled as a sidecar yet. Start it before testing commands in the UI. Never package API keys in the desktop bundle.
