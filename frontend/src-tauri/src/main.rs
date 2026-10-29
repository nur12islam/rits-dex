#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{
    io::{Read, Write},
    net::{SocketAddr, TcpStream},
    process::{Child, Command, Stdio},
    sync::Mutex,
    thread,
    time::{Duration, Instant},
};
use tauri::{Manager, RunEvent};

struct ManagedBackend(Mutex<Option<Child>>);

fn backend_health_check(address: &SocketAddr) -> bool {
    let Ok(mut stream) = TcpStream::connect_timeout(address, Duration::from_millis(250)) else {
        return false;
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(350)));
    let request = b"GET /health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n";
    if stream.write_all(request).is_err() {
        return false;
    }
    let mut response = String::new();
    if stream.read_to_string(&mut response).is_err() {
        return false;
    }
    response.starts_with("HTTP/1.1 200") && response.contains("rits-local-core")
}

fn wait_for_backend(child: &mut Child) -> Result<(), String> {
    let address: SocketAddr = "127.0.0.1:8765".parse().expect("valid loopback address");
    let deadline = Instant::now() + Duration::from_secs(12);
    while Instant::now() < deadline {
        if let Some(status) = child.try_wait().map_err(|e| format!("Could not inspect backend process: {e}"))? {
            return Err(format!("RITS backend exited before becoming healthy (status: {status}). Check Python dependencies and port 8765."));
        }
        if backend_health_check(&address) {
            return Ok(());
        }
        thread::sleep(Duration::from_millis(200));
    }
    Err("RITS backend did not pass its /health check on 127.0.0.1:8765 within 12 seconds".to_string())
}

fn start_backend(app: &tauri::App) -> Result<Child, String> {
    let address: SocketAddr = "127.0.0.1:8765".parse().expect("valid loopback address");
    if TcpStream::connect_timeout(&address, Duration::from_millis(150)).is_ok() {
        return Err("Port 8765 is already in use. Close the other local service before launching RITS; RITS will not attach to or terminate an unrelated process.".to_string());
    }

    #[cfg(debug_assertions)]
    {
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
            format!("Could not start Python backend. Activate the project virtual environment and install backend dependencies first: {e}")
        });
    }

    #[cfg(not(debug_assertions))]
    {
        let resource_dir = app.path().resource_dir().map_err(|e| e.to_string())?;
        let executable = resource_dir.join("rits-backend.exe");
        if !executable.is_file() {
            return Err(format!(
                "Bundled backend executable is missing: {}. Rebuild the app with the Windows backend bundle step.",
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
                    if let Some(state) = app.try_state::<ManagedBackend>() {
                        if let Ok(mut slot) = state.0.lock() {
                            if let Some(child) = slot.as_mut() {
                                if let Err(error) = wait_for_backend(child) {
                                    eprintln!("RITS backend startup failed: {error}");
                                    let _ = child.kill();
                                    let _ = child.wait();
                                    *slot = None;
                                }
                            }
                        }
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
