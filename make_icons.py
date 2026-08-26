#!/usr/bin/env python3
"""Generate simple gradient PNG icons for the extension (no external deps)."""
import struct, zlib, os, math

def lerp(a, b, t):
    return int(a + (b - a) * t)

def make_png(size, path):
    # Accent gradient: #6d8bff -> #8a6dff, with a soft "play"/spark glyph.
    c1 = (0x6d, 0x8b, 0xff)
    c2 = (0x8a, 0x6d, 0xff)
    cx, cy = size / 2, size / 2
    r = size * 0.30  # glyph radius

    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0 for each scanline
        for x in range(size):
            t = (x + y) / (2 * size)
            rr, gg, bb = lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t)
            a = 255
            # rounded corners
            corner = size * 0.18
            dx = max(corner - x, x - (size - 1 - corner), 0)
            dy = max(corner - y, y - (size - 1 - corner), 0)
            if math.hypot(dx, dy) > corner:
                a = 0
            # white play triangle in the middle
            inx = x - cx
            iny = y - cy
            if -r < inx < r * 0.7 and abs(iny) < (r - (inx + r) * 0.5):
                rr, gg, bb = 255, 255, 255
            raw += bytes((rr, gg, bb, a))

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(bytes(raw), 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, len(png), "bytes")

os.makedirs("icons", exist_ok=True)
for s in (16, 48, 128):
    make_png(s, f"icons/icon{s}.png")
