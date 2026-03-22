"""Screenshot capture via mss."""

import mss
from PIL import Image


def take_screenshot() -> Image.Image:
    """Capture the primary monitor and return a PIL Image."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
