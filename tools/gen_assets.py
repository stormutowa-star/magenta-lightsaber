#!/usr/bin/env python3
"""Generate the lightsaber textures and item models.

Run from the project root:  python tools/gen_assets.py
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "src" / "main" / "resources" / "assets" / "magenta_lightsaber"
TEXTURES = ASSETS / "textures" / "item"
MODELS = ASSETS / "models" / "item"
MODID = "magenta_lightsaber"

# Material regions inside the 32x32 hilt texture (UV units 0..16).
UV = {
    "gold": [0.0, 0.0, 8.0, 8.0],
    "silver": [8.0, 0.0, 16.0, 8.0],
    "grip": [0.0, 8.0, 8.0, 16.0],
    "accent": [8.0, 8.0, 16.0, 16.0],
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mix(a, b, t: float):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def make_hilt_texture() -> Image.Image:
    rng = random.Random(20261021)
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
    px = img.load()

    # --- gold quadrant -----------------------------------------------------
    for x in range(16):
        edge = 1.0 - abs(x - 7.5) / 8.0
        highlight = math.exp(-((x - 6.2) / 2.3) ** 2)
        base = mix((104, 68, 7), (235, 190, 72), 0.35 + 0.45 * edge)
        base = mix(base, (255, 241, 166), 0.55 * highlight)
        streak = rng.uniform(-8, 8)
        for y in range(16):
            r, g, b = base
            # machined grooves
            if y in (3, 11):
                r, g, b = int(r * 0.62), int(g * 0.62), int(b * 0.62)
            elif y in (4, 12):
                r, g, b = clamp(r * 1.18, 0, 255), clamp(g * 1.18, 0, 255), clamp(b * 1.18, 0, 255)
            n = streak + rng.uniform(-4, 4)
            px[x, y] = (int(clamp(r + n, 0, 255)), int(clamp(g + n * 0.9, 0, 255)),
                        int(clamp(b + n * 0.5, 0, 255)), 255)

    # --- silver quadrant ---------------------------------------------------
    for x in range(16):
        edge = 1.0 - abs(x - 7.5) / 8.0
        highlight = math.exp(-((x - 9.0) / 2.1) ** 2)
        base = mix((82, 89, 103), (196, 203, 216), 0.28 + 0.55 * edge)
        base = mix(base, (248, 251, 255), 0.65 * highlight)
        streak = rng.uniform(-7, 7)
        for y in range(16):
            r, g, b = base
            if y in (2, 13):
                r, g, b = int(r * 0.70), int(g * 0.70), int(b * 0.72)
            n = streak + rng.uniform(-3, 3)
            px[16 + x, y] = (int(clamp(r + n, 0, 255)), int(clamp(g + n, 0, 255)),
                             int(clamp(b + n * 1.15, 0, 255)), 255)

    # --- dark grip quadrant ------------------------------------------------
    for x in range(16):
        edge = 1.0 - abs(x - 7.5) / 8.0
        base = mix((16, 17, 22), (54, 56, 68), 0.20 + 0.65 * edge)
        for y in range(16):
            r, g, b = base
            # grip ribs run around the hilt (constant V)
            rib = y % 4
            if rib == 0:
                r, g, b = clamp(r * 1.45 + 10, 0, 255), clamp(g * 1.45 + 10, 0, 255), clamp(b * 1.5 + 12, 0, 255)
            elif rib == 3:
                r, g, b = r * 0.55, g * 0.55, b * 0.60
            px[x, 16 + y] = (int(r), int(g), int(b), 255)

        # small magenta energy slit in the middle of the grip
        for y in (14, 15):
            if x in (5, 6, 9, 10):
                px[x, 16 + y] = (255, 82, 242, 255)
            elif 4 <= x <= 11:
                px[x, 16 + y] = (126, 0, 122, 255)

    # --- accent / emitter quadrant -----------------------------------------
    for x in range(16):
        for y in range(16):
            edge = 1.0 - abs(x - 7.5) / 8.0
            base = mix((8, 8, 12), (34, 34, 44), 0.35 * edge)
            px[16 + x, 16 + y] = (*base, 255)

    # magenta plasma ring
    for y in range(6, 10):
        intensity = 0.55 + 0.45 * math.sin((y - 5) / 4 * math.pi)
        for x in range(16):
            core = math.exp(-((x - 7.5) / 3.4) ** 2)
            r = int(150 + 105 * core * intensity)
            g = int(0 + 70 * core * intensity)
            b = int(145 + 105 * core * intensity)
            px[16 + x, 16 + y] = (min(r, 255), min(g, 255), min(b, 255), 255)

    # gold pinstripes around the plasma ring
    for y in (4, 12):
        for x in range(16):
            px[16 + x, 16 + y] = (226, 174, 54, 255)
    for y in (5, 11):
        for x in range(16):
            px[16 + x, 16 + y] = (118, 82, 18, 255)

    return img


def make_blade_texture() -> Image.Image:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for x in range(16):
        d = abs(x - 7.5)
        if d <= 0.9:
            color = (255, 255, 255)
        elif d <= 2.1:
            color = (255, 230, 255)
        elif d <= 3.6:
            color = (255, 125, 255)
        elif d <= 5.4:
            color = (255, 36, 246)
        else:
            color = (186, 0, 205)
        for y in range(16):
            pulse = 1.0 + 0.045 * math.sin(y * 1.9)
            px[x, y] = (
                int(clamp(color[0] * pulse, 0, 255)),
                int(clamp(color[1] * pulse, 0, 255)),
                int(clamp(color[2] * pulse, 0, 255)),
                255,
            )
    return img


def make_glow_texture(outer: bool) -> Image.Image:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    for x in range(32):
        d = abs(x - 15.5) / 16.0
        if outer:
            if d < 0.10:
                alpha = 0.0
            elif d < 0.34:
                alpha = 0.22 * ((d - 0.10) / 0.24)
            else:
                alpha = 0.22 * (1.0 - (d - 0.34) / 0.66)
            color = (255, 38, 248)
        else:
            if d < 0.16:
                alpha = 0.0
            elif d < 0.30:
                alpha = 0.52 * ((d - 0.16) / 0.14)
            elif d < 0.72:
                alpha = 0.52 * (1.0 - 0.55 * (d - 0.30) / 0.42)
            else:
                alpha = 0.234 * (1.0 - (d - 0.72) / 0.28)
            color = (255, 52, 250) if d < 0.5 else (232, 0, 230)
        alpha = clamp(alpha, 0.0, 1.0)
        for y in range(32):
            shimmer = 1.0 + 0.05 * math.sin(y * 0.8 + x * 0.3)
            px[x, y] = (
                int(clamp(color[0] * shimmer, 0, 255)),
                int(clamp(color[1] * shimmer, 0, 255)),
                int(clamp(color[2] * shimmer, 0, 255)),
                int(alpha * 255),
            )
    return img


def texture(name: str) -> str:
    return f"{MODID}:item/{name}"


def faces(material: str, shade: bool = True) -> dict:
    uv = UV[material]
    result = {}
    for direction in ("down", "up", "north", "south", "west", "east"):
        result[direction] = {"texture": "#hilt", "uv": uv}
    return result


def blade_faces(tex: str, shade: bool = False) -> dict:
    return {
        direction: {"texture": tex, "uv": [0.0, 0.0, 16.0, 16.0]}
        for direction in ("down", "up", "north", "south", "west", "east")
    }


def element(name: str, a, b, material: str) -> dict:
    return {
        "name": name,
        "from": list(a),
        "to": list(b),
        "faces": faces(material),
        "shade": True,
    }


def blade_element(name: str, a, b, tex: str) -> dict:
    return {
        "name": name,
        "from": list(a),
        "to": list(b),
        "faces": blade_faces(tex),
        "shade": False,
    }


def hilt_elements() -> list[dict]:
    return [
        element("pommel_cap", (-2.4, 0.0, -2.4), (2.4, 1.0, 2.4), "gold"),
        element("pommel_inset", (-1.5, -0.2, -1.5), (1.5, 0.35, 1.5), "grip"),
        element("pommel_ring", (-2.1, 0.98, -2.1), (2.1, 1.72, 2.1), "silver"),
        element("grip", (-1.65, 1.68, -1.65), (1.65, 4.22, 1.65), "grip"),

        # Four slim gold inlays run along the grip.
        element("grip_inlay_n", (-0.24, 1.95, 1.60), (0.24, 4.12, 1.76), "gold"),
        element("grip_inlay_s", (-0.24, 1.95, -1.76), (0.24, 4.12, -1.60), "gold"),
        element("grip_inlay_w", (-1.76, 1.95, -0.24), (-1.60, 4.12, 0.24), "gold"),
        element("grip_inlay_e", (1.60, 1.95, -0.24), (1.76, 4.12, 0.24), "gold"),

        element("gold_band_low", (-2.05, 2.65, -2.05), (2.05, 2.95, 2.05), "gold"),
        element("gold_band_mid", (-2.05, 4.18, -2.05), (2.05, 4.52, 2.05), "gold"),
        element("silver_band_low", (-2.1, 4.48, -2.1), (2.1, 5.02, 2.1), "silver"),
        element("crystal_ring", (-2.25, 4.98, -2.25), (2.25, 5.27, 2.25), "accent"),
        element("silver_band_high", (-2.1, 5.23, -2.1), (2.1, 5.72, 2.1), "silver"),
        element("silver_body", (-2.0, 5.68, -2.0), (2.0, 6.52, 2.0), "silver"),
        element("gold_band_high", (-2.2, 6.15, -2.2), (2.2, 6.45, 2.2), "gold"),
        element("emitter_base", (-2.4, 6.48, -2.4), (2.4, 7.22, 2.4), "gold"),
        element("emitter_collar", (-2.0, 7.18, -2.0), (2.0, 7.52, 2.0), "silver"),
        element("emitter_core", (-1.55, 7.48, -1.55), (1.55, 7.87, 1.55), "accent"),

        # Four gold claws frame the blade.
        element("claw_w", (-2.95, 6.85, -1.35), (-2.38, 8.05, 1.35), "gold"),
        element("claw_e", (2.38, 6.85, -1.35), (2.95, 8.05, 1.35), "gold"),
        element("claw_n", (-1.35, 6.85, 2.38), (1.35, 8.05, 2.95), "gold"),
        element("claw_s", (-1.35, 6.85, -2.95), (1.35, 8.05, -2.38), "gold"),
    ]


def blade_elements() -> list[dict]:
    return [
        blade_element("blade_core", (-0.9, 7.25, -0.9), (0.9, 23.8, 0.9), "#blade"),
        blade_element("blade_tip_1", (-0.64, 23.8, -0.64), (0.64, 24.3, 0.64), "#blade"),
        blade_element("blade_tip_2", (-0.34, 24.3, -0.34), (0.34, 24.56, 0.34), "#blade"),
        blade_element("blade_glow", (-2.1, 7.7, -2.1), (2.1, 24.0, 2.1), "#glow"),
        blade_element("blade_glow_tip", (-1.2, 24.0, -1.2), (1.2, 24.35, 1.2), "#glow"),
        blade_element("blade_aura", (-3.1, 7.9, -3.1), (3.1, 23.9, 3.1), "#aura"),
        blade_element("blade_aura_tip", (-1.7, 23.9, -1.7), (1.7, 24.2, 1.7), "#aura"),
    ]


def display(active: bool) -> dict:
    if active:
        gui_scale = 0.66
        gui_translation = [8.0, (0.5 - gui_scale * (24.56 / 2 / 16)) * 16, 0.0]
    else:
        gui_scale = 1.2
        gui_translation = [8.0, (0.5 - gui_scale * (8.05 / 2 / 16)) * 16, 0.0]

    return {
        "gui": {
            "rotation": [0, 0, 0],
            "translation": [round(v, 4) for v in gui_translation],
            "scale": [gui_scale] * 3,
        },
        "ground": {
            "rotation": [0, 0, 0],
            "translation": [0, 2, 0],
            "scale": [0.5, 0.5, 0.5],
        },
        "fixed": {
            "rotation": [0, 0, 0],
            "translation": [0, 0, 0],
            "scale": [0.5, 0.5, 0.5],
        },
        "head": {
            "rotation": [0, 0, 0],
            "translation": [0, 0, 0],
            "scale": [0.35, 0.35, 0.35],
        },
        "thirdperson_righthand": {
            "rotation": [0, -90, 55],
            "translation": [0, 4, 0.8],
            "scale": [0.8, 0.8, 0.8],
        },
        "thirdperson_lefthand": {
            "rotation": [0, 90, -55],
            "translation": [0, 4, 0.8],
            "scale": [0.8, 0.8, 0.8],
        },
        "firstperson_righthand": {
            "rotation": [0, -90, 22],
            "translation": [1.0, 3.0, 0.8],
            "scale": [0.62, 0.62, 0.62],
        },
        "firstperson_lefthand": {
            "rotation": [0, 90, -22],
            "translation": [1.0, 3.0, 0.8],
            "scale": [0.62, 0.62, 0.62],
        },
    }


def base_model(active: bool) -> dict:
    elements = hilt_elements()
    textures = {
        "particle": texture("blade"),
        "hilt": texture("hilt"),
        "blade": texture("blade"),
    }

    if active:
        elements = elements + blade_elements()
        textures.update({
            "blade": texture("blade"),
            "glow": texture("blade_glow"),
            "aura": texture("blade_glow_outer"),
        })

    model = {
        "parent": "minecraft:item/handheld",
        "gui_light": "front",
        "textures": textures,
        "elements": elements,
        "display": display(active),
    }

    if not active:
        model["overrides"] = [{
            "predicate": {f"{MODID}:active": 1.0},
            "model": f"{MODID}:item/lightsaber_on",
        }]

    return model


def make_logo() -> Image.Image:
    logo = Image.new("RGBA", (128, 128), (9, 7, 14, 255))
    px = logo.load()

    # subtle purple vignette
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - 64, y - 64) / 92.0
            if d < 1.0:
                add = int(24 * (1.0 - d))
                r, g, b, a = px[x, y]
                px[x, y] = (min(r + add, 255), g, min(b + add + 14, 255), a)

    # blade glow
    for y in range(6, 82):
        for x in range(34, 95):
            dx = abs(x - 64.5) / 30.0
            alpha = int(95 * max(0.0, 1.0 - dx) ** 1.6)
            if alpha:
                r, g, b, a = px[x, y]
                px[x, y] = (min(r + int(alpha * 0.9), 255), g, min(b + int(alpha * 0.95), 255), a)

    # blade
    for y in range(8, 80):
        for x in range(58, 71):
            d = abs(x - 64.5)
            if d < 2:
                color = (255, 255, 255)
            elif d < 4:
                color = (255, 165, 255)
            elif d < 6:
                color = (255, 32, 245)
            else:
                color = (185, 0, 204)
            px[x, y] = (*color, 255)

    # hilt
    hilt_top = 80
    hilt_bottom = 120
    for y in range(hilt_top, hilt_bottom):
        t = (y - hilt_top) / (hilt_bottom - hilt_top)
        if 0.0 <= t < 0.10:
            color = (226, 174, 54)       # gold pommel
        elif 0.10 <= t < 0.20:
            color = (170, 178, 192)      # silver ring
        elif 0.20 <= t < 0.62:
            color = (36, 38, 48)         # grip
        elif 0.62 <= t < 0.70:
            color = (226, 174, 54)       # gold band
        elif 0.70 <= t < 0.76:
            color = (255, 70, 240)       # crystal ring
        elif 0.76 <= t < 0.92:
            color = (190, 198, 212)      # silver body
        else:
            color = (224, 170, 50)       # emitter
        half = 6 if 0.20 <= t < 0.62 else 8
        for x in range(64 - half, 64 + half):
            edge = abs(x - 64.5) / half
            shade = 0.62 + 0.50 * (1.0 - edge)
            px[x, y] = (
                int(clamp(color[0] * shade, 0, 255)),
                int(clamp(color[1] * shade, 0, 255)),
                int(clamp(color[2] * shade, 0, 255)),
                255,
            )
        # dark grip ribs
        if 0.24 <= t < 0.60 and int((y - hilt_top) / 3) % 2 == 0:
            for x in range(64 - 6, 64 + 6):
                r, g, b, a = px[x, y]
                px[x, y] = (int(r * 0.72), int(g * 0.72), int(b * 0.78), a)

    # emitter claws
    for x in range(52, 58):
        for y in range(76, 88):
            px[x, y] = (205, 152, 40, 255)
    for x in range(71, 77):
        for y in range(76, 88):
            px[x, y] = (205, 152, 40, 255)

    return logo


def main() -> None:
    TEXTURES.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)

    make_hilt_texture().save(TEXTURES / "hilt.png")
    make_blade_texture().save(TEXTURES / "blade.png")
    make_glow_texture(False).save(TEXTURES / "blade_glow.png")
    make_glow_texture(True).save(TEXTURES / "blade_glow_outer.png")

    (MODELS / "lightsaber.json").write_text(json.dumps(base_model(False), indent=2) + "\n", encoding="utf-8")
    (MODELS / "lightsaber_on.json").write_text(json.dumps(base_model(True), indent=2) + "\n", encoding="utf-8")
    make_logo().save(ROOT / "src" / "main" / "resources" / "logo.png")

    print("Generated textures and models.")


if __name__ == "__main__":
    main()
