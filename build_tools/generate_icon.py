"""Generate the ZScoreToolbox application icon (assets/icon.ico).

Uses only Pillow — no external dependencies required.
Run from the repository root:

    py build_tools/generate_icon.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Output path (relative to repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent
ICON_PATH = REPO_ROOT / "assets" / "icon.ico"

# Required .ico sizes
SIZES = [16, 32, 48, 64, 128, 256]

# Colours
BG = "#1a1a2e"
CYAN = "#00bfff"
CURVE_COLOR = "#0080aa"


def _normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Standard normal PDF."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def _draw_icon(size: int) -> Image.Image:
    """Render the icon at *size* x *size* pixels."""
    img = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(img)

    # --- Bell curve (bottom third of the icon) ---
    curve_y_top = int(size * 0.55)
    curve_y_bottom = int(size * 0.85)
    curve_height = curve_y_bottom - curve_y_top
    margin_x = int(size * 0.10)

    # Sample the normal PDF across the icon width
    n_points = max(size, 60)
    xs = [margin_x + (size - 2 * margin_x) * i / (n_points - 1) for i in range(n_points)]
    # Map pixel x -> standard-normal x range [-3.2, 3.2]
    z_values = [-3.2 + 6.4 * i / (n_points - 1) for i in range(n_points)]
    pdf_values = [_normal_pdf(z) for z in z_values]
    pdf_max = max(pdf_values)

    points = []
    for px, pdf_val in zip(xs, pdf_values):
        # Normalise so peak just touches curve_y_top, baseline at curve_y_bottom
        ny = curve_y_bottom - (pdf_val / pdf_max) * curve_height
        points.append((px, ny))

    curve_width = max(1, size // 50 + 1)
    if len(points) >= 2:
        draw.line(points, fill=CURVE_COLOR, width=curve_width)

    # --- Bold "Z" letter (upper portion) ---
    # Try to use a built-in bold font; fall back to default bitmap font
    z_height_target = int(size * 0.50)
    font = None
    for font_name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf",
                       "LiberationSans-Bold.ttf", "FreeSansBold.ttf"):
        try:
            font = ImageFont.truetype(font_name, z_height_target)
            break
        except OSError:
            continue

    if font is None:
        # Last resort: default bitmap font (small but functional)
        font = ImageFont.load_default()

    # Measure and centre the Z
    bbox = draw.textbbox((0, 0), "Z", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = int(size * 0.06) - bbox[1]  # slightly below the top edge

    draw.text((tx, ty), "Z", fill=CYAN, font=font)

    return img


def generate() -> Path:
    """Generate *assets/icon.ico* containing all required sizes."""
    ICON_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Render the largest size, then let Pillow resample for the .ico
    base = _draw_icon(max(SIZES))
    base.save(
        str(ICON_PATH),
        format="ICO",
        sizes=[(s, s) for s in SIZES],
    )
    print(f"Icon saved to {ICON_PATH}  ({', '.join(f'{s}x{s}' for s in SIZES)})")
    return ICON_PATH


if __name__ == "__main__":
    generate()
