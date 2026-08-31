import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "aria-7-character-field.gif"
LIGHT_OUTPUT = ROOT / "assets" / "aria-7-character-field-light.gif"
DARK_OUTPUT = ROOT / "assets" / "aria-7-character-field-dark.gif"
WIDTH = 960
HEIGHT = 500
FRAME_COUNT = 14
FRAME_DURATION = 120
CELL_WIDTH = 12
CELL_HEIGHT = 18
LIGHT_BACKGROUND = "#ffffff"
LIGHT_PALETTE = [
    "#b8e2ff",
    "#93d1ff",
    "#62baff",
    "#299cff",
    "#087ce8",
    "#0758b2",
    "#082f58",
]
DARK_BACKGROUND = "#161b22"
DARK_PALETTE = [
    "#34536f",
    "#4d7fa5",
    "#67a6cf",
    "#84c8f1",
    "#42a9ed",
    "#2388d2",
    "#c0e9ff",
]
CHARACTERS = ["-", "+", "/", "(", ")", "*", "▲", "K", "#", "⬢"]
FIELD_FONT_PATH = Path(r"C:\Windows\Fonts\consola.ttf")
LABEL_FONT_PATH = Path(r"C:\Windows\Fonts\consolab.ttf")


def clamp(value, minimum=0.0, maximum=1.0):
    return min(maximum, max(minimum, value))


def smoothstep(edge0, edge1, value):
    t = clamp((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def hash_value(x, y):
    value = math.sin(x * 127.1 + y * 311.7) * 43758.5453123
    return value - math.floor(value)


def field_value(u, v, phase):
    centered_y = v - 0.5
    drift = 0.055 * math.sin(phase * 0.75 + v * 8.3) + 0.032 * math.sin(phase * 1.2 - v * 19.0)
    warp = 0.105 * math.sin(v * 8.2 + phase) + 0.045 * math.sin(v * 21.0 - phase * 1.6)
    diagonal = 0.032 * math.sin(u * 16.0 + v * 13.0 - phase * 1.1)
    density = smoothstep(0.025, 0.98, u + warp + drift + diagonal)
    swirl_x = u - 0.58 - 0.055 * math.sin(phase)
    swirl_y = centered_y + 0.08 * math.sin(phase * 0.72)
    radius = math.sqrt((swirl_x * 1.18) ** 2 + swirl_y ** 2)
    angle = math.atan2(swirl_y, swirl_x)
    rings = 0.11 * math.sin(radius * 40.0 - phase * 1.35 + angle * 2.8)
    stream = 0.075 * math.sin(v * 27.0 - u * 8.0 + phase * 0.9)
    upper_flow = math.exp(-((u - 0.63) / 0.24) ** 2 - ((v - 0.2) / 0.32) ** 2)
    lower_flow = math.exp(-((u - 0.54) / 0.28) ** 2 - ((v - 0.78) / 0.28) ** 2)
    pockets = 0.09 * upper_flow * math.sin(v * 30.0 + phase * 1.7) + 0.075 * lower_flow * math.cos(v * 34.0 - phase)
    noise = (hash_value(math.floor(u * 89), math.floor(v * 61)) - 0.5) * 0.028
    return clamp(density * 0.92 + rings + stream + pockets + noise)


def character_for(value, column, row, frame):
    variation = hash_value(column * 1.37 + math.floor(frame * 0.35), row * 1.91)
    if value < 0.18:
        return "-" if variation <= 0.48 else "+"
    if value < 0.29:
        return "/" if variation <= 0.5 else "+"
    if value < 0.42:
        return "(" if variation <= 0.53 else ")"
    if value < 0.56:
        return "*" if variation <= 0.5 else "("
    if value < 0.68:
        return "▲" if variation <= 0.45 else "*"
    if value < 0.79:
        return "K" if variation <= 0.44 else "▲"
    if value < 0.9:
        return "#" if variation <= 0.35 else "K"
    return "⬢" if variation <= 0.18 else "#"


def draw_label(draw, frame, background, palette):
    color = palette[-1] if frame % 3 else palette[-2]
    draw.text(
        (60, 68),
        "Aria-7",
        font=LABEL_FONT,
        fill=color,
        stroke_width=1,
        stroke_fill=background,
    )


def make_frame(frame, background, palette):
    image = Image.new("RGB", (WIDTH, HEIGHT), background)
    draw = ImageDraw.Draw(image)
    phase = frame / FRAME_COUNT * math.tau
    for row in range(math.ceil(HEIGHT / CELL_HEIGHT) + 1):
        y = (row - 0.9) * CELL_HEIGHT
        v = y / HEIGHT
        for column in range(math.ceil(WIDTH / CELL_WIDTH) + 1):
            x = (column - 0.1) * CELL_WIDTH
            u = x / WIDTH
            value = field_value(u, v, phase)
            visibility = smoothstep(0.085, 0.2, value)
            dropout = hash_value(column + 17, row + 31 + frame * 0.37)
            if visibility < 0.03 or dropout > visibility * 1.08:
                continue
            level = min(len(palette) - 1, max(0, int(value * len(palette))))
            character = character_for(value, column, row, frame)
            color = palette[level]
            draw.text((x, y + CELL_HEIGHT * 0.5), character, font=FIELD_FONT, fill=color, anchor="mm")
    draw_label(draw, frame, background, palette)
    return image


FIELD_FONT = ImageFont.truetype(str(FIELD_FONT_PATH), 15)
LABEL_FONT = ImageFont.truetype(str(LABEL_FONT_PATH), 54)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    for output, background, palette in [
        (OUTPUT, LIGHT_BACKGROUND, LIGHT_PALETTE),
        (LIGHT_OUTPUT, LIGHT_BACKGROUND, LIGHT_PALETTE),
        (DARK_OUTPUT, DARK_BACKGROUND, DARK_PALETTE),
    ]:
        frames = [make_frame(frame, background, palette) for frame in range(FRAME_COUNT)]
        frames[0].save(
            output,
            save_all=True,
            append_images=frames[1:],
            duration=FRAME_DURATION,
            loop=0,
            optimize=False,
            disposal=2,
        )


if __name__ == "__main__":
    main()
