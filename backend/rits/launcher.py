"""Entry point used when packaging the local API as a Windows executable."""
import uvicorn


def main() -> None:
    # The local service is restricted to loopback and does not expose a shell.
    uvicorn.run(
        "rits.app:app",
        host="127.0.0.1",
        port=8765,
        log_level="warning",
        access_log=False,
    )


if __name__ == "__main__":
    main()
