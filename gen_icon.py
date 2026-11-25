import os
import struct
import zlib

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "app", "src", "main", "res")

# “斤”字笔画（归一化坐标）
STROKES = [
    (0.48, 0.16, 0.24, 0.40),
    (0.40, 0.30, 0.16, 0.82),
    (0.20, 0.44, 0.84, 0.44),
    (0.56, 0.44, 0.56, 0.84),
]


def dist_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    qx, qy = x1 + t * dx, y1 + t * dy
    return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5


def rounded(x, y, size, radius):
    if x < radius and y < radius:
        return (x - radius) ** 2 + (y - radius) ** 2 <= radius ** 2
    if x > size - 1 - radius and y < radius:
        return (x - (size - 1 - radius)) ** 2 + (y - radius) ** 2 <= radius ** 2
    if x < radius and y > size - 1 - radius:
        return (x - radius) ** 2 + (y - (size - 1 - radius)) ** 2 <= radius ** 2
    if x > size - 1 - radius and y > size - 1 - radius:
        return (x - (size - 1 - radius)) ** 2 + (y - (size - 1 - radius)) ** 2 <= radius ** 2
    return True


def chunk(tag, data):
    body = tag + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def make_icon(path, size):
    radius = size * 0.22
    line = size * 0.075
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter: none
        for x in range(size):
            if not rounded(x, y, size, radius):
                raw.extend((0, 0, 0, 0))
                continue
            in_stroke = any(
                dist_seg(x + 0.5, y + 0.5, a * size, b * size, c * size, d * size) <= line
                for a, b, c, d in STROKES
            )
            if in_stroke:
                raw.extend((255, 255, 255, 255))
            else:
                raw.extend((15, 118, 110, 255))  # teal
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print("generated", path, size)


for density, size in [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144)]:
    make_icon(os.path.join(RES, "mipmap-" + density, "ic_launcher.png"), size)
