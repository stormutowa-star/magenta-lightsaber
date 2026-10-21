#!/usr/bin/env python3
"""Quick-and-dirty software preview for the item model (not part of the mod)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "src" / "main" / "resources" / "assets" / "magenta_lightsaber"
MODELS = ASSETS / "models" / "item"
TEXTURES = ASSETS / "textures" / "item"
OUT = ROOT / "preview.png"

SCALE = 18
PAD = 10
SUPERSAMPLE = 2

FACE_AXES = {
    "west": ("z", "y", True),
    "east": ("z", "y", False),
    "north": ("x", "y", False),
    "south": ("x", "y", True),
    "up": ("x", "z", True),
    "down": ("x", "z", False),
}


def load_model(name: str):
    model = json.loads((MODELS / f"{name}.json").read_text(encoding="utf-8"))
    textures = {}
    for key, value in model["textures"].items():
        if not value.startswith("#"):
            path = value.split(":", 1)[1]
            textures[key] = Image.open(ASSETS / "textures" / f"{path}.png").convert("RGBA")
    return model, textures


def face_quad(el, direction):
    fx, fy, fz = el["from"]
    tx, ty, tz = el["to"]
    if direction == "west":
        return [(fx, ty, fz), (fx, ty, tz), (fx, fy, tz), (fx, fy, fz)]
    if direction == "east":
        return [(tx, ty, tz), (tx, ty, fz), (tx, fy, fz), (tx, fy, tz)]
    if direction == "north":
        return [(tx, ty, fz), (fx, ty, fz), (fx, fy, fz), (tx, fy, fz)]
    if direction == "south":
        return [(fx, ty, tz), (tx, ty, tz), (tx, fy, tz), (fx, fy, tz)]
    if direction == "up":
        return [(fx, ty, fz), (tx, ty, fz), (tx, ty, tz), (fx, ty, tz)]
    if direction == "down":
        return [(fx, fy, tz), (tx, fy, tz), (tx, fy, fz), (fx, fy, fz)]
    raise ValueError(direction)


def normalize(v):
    l = math.sqrt(sum(c * c for c in v))
    return tuple(c / l for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rotate_view(p, yaw, pitch):
    x, y, z = p
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    y1 = y
    y2 = y1 * cp - z1 * sp
    z2 = y1 * sp + z1 * cp
    return x1, y2, z2


def uv_for(direction, point, el):
    fx, fy, fz = el["from"]
    tx, ty, tz = el["to"]
    x, y, z = point
    if direction in ("west", "east"):
        u = (z - fz) / (tz - fz) if direction == "west" else (tz - z) / (tz - fz)
        v = (ty - y) / (ty - fy)
    elif direction in ("north", "south"):
        u = (tx - x) / (tx - fx) if direction == "north" else (x - fx) / (tx - fx)
        v = (ty - y) / (ty - fy)
    elif direction == "up":
        u = (x - fx) / (tx - fx)
        v = (z - fz) / (tz - fz)
    else:
        u = (x - fx) / (tx - fx)
        v = (tz - z) / (tz - fz)
    return u, v


def sample(tex: Image.Image, u: float, v: float, w: int, h: int):
    x = min(w - 1, max(0, int(u * w)))
    y = min(h - 1, max(0, int(v * h)))
    return tex.getpixel((x, y))


def render(model_name: str, yaw_deg: float, pitch_deg: float, target_height_px: int, label: str):
    model, textures = load_model(model_name)
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    # Fit the model
    pts = []
    for el in model["elements"]:
        for x in (el["from"][0], el["to"][0]):
            for y in (el["from"][1], el["to"][1]):
                for z in (el["from"][2], el["to"][2]):
                    pts.append(rotate_view((x, y, z), yaw, pitch))
    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    height = max_y - min_y
    scale = (target_height_px * SUPERSAMPLE) / max(height, 0.1)
    width_px = int((max_x - min_x) * scale) + 2 * PAD * SUPERSAMPLE
    height_px = target_height_px * SUPERSAMPLE + 2 * PAD * SUPERSAMPLE

    canvas = Image.new("RGBA", (width_px, height_px), (10, 8, 16, 255))
    draw = Image.new("RGBA", canvas.size, (0, 0, 0, 0))

    # Collect faces with depth
    faces = []
    view_dir = normalize((0, 0, -1))
    for el in model["elements"]:
        # Light from the front-upper-left of the camera.
        for direction, face in el["faces"].items():
            quad = face_quad(el, direction)
            normal = {
                "west": (-1, 0, 0), "east": (1, 0, 0),
                "north": (0, 0, -1), "south": (0, 0, 1),
                "up": (0, 1, 0), "down": (0, -1, 0),
            }[direction]
            # Rotate normal into view space (orthographic camera looks along -Z)
            rn = rotate_view(normal, yaw, pitch)
            if dot(rn, view_dir) <= 0.001:
                continue
            center = tuple(sum(p[i] for p in quad) / 4 for i in range(3))
            depth = rotate_view(center, yaw, pitch)[2]
            faces.append((depth, el, direction, quad, normal))

    faces.sort(key=lambda f: f[0])

    light = normalize((-0.45, 0.8, -0.5))
    for depth, el, direction, quad, normal in faces:
        tex_key = el["faces"][direction]["texture"]
        tex = textures[tex_key[1:]]
        uv = el["faces"][direction]["uv"]
        tw, th = tex.size
        shade = 0.72 + 0.28 * max(0.0, dot(normal, light))
        if not el.get("shade", True):
            shade = 1.0

        # Subdivide the face for texture detail.
        steps = 4
        for iu in range(steps):
            for iv in range(steps):
                sub = []
                for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    u = (iu + du) / steps
                    v = (iv + dv) / steps
                    # Interpolate the quad corners (v measured from the top of the face).
                    p = []
                    for c in range(3):
                        top = quad[0][c] * (1 - u) + quad[1][c] * u
                        bottom = quad[3][c] * (1 - u) + quad[2][c] * u
                        p.append(top * (1 - v) + bottom * v)
                    sub.append(tuple(p))
                # The texture V is top-down; our v is top-down already.
                uc = (iu + 0.5) / steps
                vc = (iv + 0.5) / steps
                r, g, b, a = sample(tex, uv[0] / 16 + uc * (uv[2] - uv[0]) / 16,
                                    uv[1] / 16 + vc * (uv[3] - uv[1]) / 16, tw, th)
                if a == 0:
                    continue
                col = (int(r * shade), int(g * shade), int(b * shade), a)
                projected = []
                for p in sub:
                    x, y, z = rotate_view(p, yaw, pitch)
                    sx = (x - min_x) * scale + PAD * SUPERSAMPLE
                    sy = (max_y - y) * scale + PAD * SUPERSAMPLE
                    projected.append((sx, sy))
                from PIL import ImageDraw
                d = ImageDraw.Draw(draw)
                d.polygon(projected, fill=col)

    canvas.alpha_composite(draw)
    canvas = canvas.resize((width_px // SUPERSAMPLE, height_px // SUPERSAMPLE), Image.Resampling.LANCZOS)

    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(canvas)
    d.text((8, 6), label, fill=(230, 210, 255, 255))
    return canvas


def main():
    a = render("lightsaber", 0, 0, 160, "OFF")
    b = render("lightsaber_on", 0, 0, 300, "ON")
    c = render("lightsaber_on", 38, 12, 300, "ON - 3/4")

    w = a.width + b.width + c.width + 40
    h = max(a.height, b.height, c.height) + 20
    sheet = Image.new("RGBA", (w, h), (8, 6, 12, 255))
    x = 10
    for im in (a, b, c):
        sheet.alpha_composite(im, (x, 10))
        x += im.width + 10
    sheet.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
