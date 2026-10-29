"""Generate a small self-contained RITS Windows icon without external dependencies.

The generated icon is a build asset, not an official brand identity.
"""
from pathlib import Path
import struct
import zlib


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def png(size: int) -> bytes:
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            dx = (x + 0.5) / size - 0.5
            dy = (y + 0.5) / size - 0.5
            in_disc = dx * dx + dy * dy < 0.19
            bar = 0.19 < x / size < 0.32 and 0.2 < y / size < 0.8
            bowl = 0.26 < x / size < 0.68 and 0.2 < y / size < 0.51
            leg = 0.47 < x / size < 0.7 and 0.48 < y / size < 0.8 and abs((x / size - 0.47) - (y / size - 0.48) * 0.65) < 0.085
            if in_disc and (bar or bowl or leg):
                rows.extend((245, 225, 225, 255))
            elif in_disc:
                rows.extend((114, 20, 42, 255))
            else:
                rows.extend((5, 5, 5, 255))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\\x89PNG\\r\\n\\x1a\\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")


def main() -> None:
    sizes = (16, 32, 48, 256)
    images = [png(size) for size in sizes]
    directory = bytearray(struct.pack("<HHH", 0, 1, len(images)))
    offset = 6 + 16 * len(images)
    for size, data in zip(sizes, images):
        directory.extend(struct.pack("<BBBBHHII", 0 if size == 256 else size, 0 if size == 256 else size, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    destination = Path(__file__).resolve().parent / "src-tauri" / "icons" / "icon.ico"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(directory) + b"".join(images))
    print(f"Generated {destination} ({destination.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
