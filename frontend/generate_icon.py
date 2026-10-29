"""Generate a valid Windows ICO containing 16, 32, 48, and 256 px DIB images."""
from pathlib import Path
import struct


def dib(size: int) -> bytes:
    pixels = bytearray()
    # ICO DIB pixel rows are stored bottom-up in BGRA order.
    for y in range(size - 1, -1, -1):
        for x in range(size):
            nx = (x + 0.5) / size
            ny = (y + 0.5) / size
            dx, dy = nx - 0.5, ny - 0.5
            disc = dx * dx + dy * dy < 0.19
            bar = 0.19 < nx < 0.32 and 0.2 < ny < 0.8
            bowl = 0.26 < nx < 0.68 and 0.2 < ny < 0.51
            leg = 0.47 < nx < 0.7 and 0.48 < ny < 0.8 and abs((nx - 0.47) - (ny - 0.48) * 0.65) < 0.085
            if disc and (bar or bowl or leg):
                red, green, blue = 245, 225, 225
            elif disc:
                red, green, blue = 114, 20, 42
            else:
                red, green, blue = 5, 5, 5
            pixels.extend((blue, green, red, 255))

    # 32-bit icons still require an AND mask; zero means opaque.
    mask_stride = ((size + 31) // 32) * 4
    mask = bytes(mask_stride * size)
    header = struct.pack("<IIIHHIIIIII", 40, size, size * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0)
    return header + bytes(pixels) + mask


def main() -> None:
    sizes = (16, 32, 48, 256)
    images = [dib(size) for size in sizes]
    directory = bytearray(struct.pack("<HHH", 0, 1, len(images)))
    offset = 6 + 16 * len(images)
    for size, data in zip(sizes, images):
        directory.extend(struct.pack("<BBBBHHII", 0 if size == 256 else size, 0 if size == 256 else size, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    destination = Path(__file__).resolve().parent / "src-tauri" / "icons" / "icon.ico"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(directory) + b"".join(images))
    print(f"Generated valid Windows icon: {destination} ({destination.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
