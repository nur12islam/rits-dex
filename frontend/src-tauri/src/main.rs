#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{
    net::{SocketAddr, TcpStream},
    process::{Child, Command, Stdio},
    sync::Mutex,
    thread,
    time::{Duration, Instant},
};
use tauri::{Manager, RunEvent};

struct ManagedBackend(Mutex<Option<Child>>);

fn wait_for_backend() -> Result<(), String> {
    let address: SocketAddr = "127.0.0.1:8765".parse().expect("valid loopback address");
    let deadline = Instant::now() + Duration::from_secs(12);
    while Instant::now() < deadline {
        if TcpStream::connect_timeout(&address, Duration::from_millis(200)).is_ok() {
            return Ok(());
        }
        thread::sleep(Duration::from_millis(200));
    }
    Err("RITS backend did not open 127.0.0.1:8765 within 12 seconds".to_string())
}

fn start_backend(app: &tauri::App) -> Result<Child, String> {
    #[cfg(debug_assertions)]
    {
        // In development, run the checked-in Python backend from the repository.
        let manifest_dir = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let backend_dir = manifest_dir.join("../../backend");
        let backend_dir = backend_dir.canonicalize().map_err(|e| {
            format!("Could not locate the backend source at {}: {e}", backend_dir.display())
        })?;
        let mut command = Command::new("python");
        command
            .args([
                "-m", "uvicorn", "rits.app:app",
                "--host", "127.0.0.1", "--port", "8765",
                "--log-level", "warning", "--no-access-log",
            ])
            .arg("--app-dir")
            .arg(&backend_dir)
            .current_dir(&backend_dir)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null());
        return command.spawn().map_err(|e| {
            format!("Could not start Python backend. Install Python 3.11+ and backend dependencies first: {e}")
        });
    }

    #[cfg(not(debug_assertions))]
    {
        let resource_dir = app.path().resource_dir().map_err(|e| e.to_string())?;
        let executable = resource_dir.join("rits-backend.exe");
        if !executable.is_file() {
            return Err(format!(
                "Bundled backend executable is missing: {}. Rebuild the app with the backend bundle step.",
                executable.display()
            ));
        }
        Command::new(&executable)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|e| format!("Could not start bundled RITS backend: {e}"))
    }
}

fn main() {
    let app = tauri::Builder::default()
        .setup(|app| {
            match start_backend(app) {
                Ok(child) => {
                    app.manage(ManagedBackend(Mutex::new(Some(child))));
                    if let Err(error) = wait_for_backend() {
                        eprintln!("{error}");
                    }
                }
                Err(error) => {
                    // Keep the UI available so it can explain how to recover.
                    eprintln!("RITS backend startup failed: {error}");
                }
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building RITS");

    app.run(|handle, event| {
        if let RunEvent::Exit = event {
            if let Some(state) = handle.try_state::<ManagedBackend>() {
                if let Ok(mut child_slot) = state.0.lock() {
                    if let Some(child) = child_slot.as_mut() {
                        let _ = child.kill();
                        let _ = child.wait();
                    }
                    *child_slot = None;
                }
            }
        }
    });
}
