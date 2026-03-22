"""Entry point: system tray icon and measurement workflow."""

import threading

from PIL import Image, ImageDraw
import pystray

from .calculator import compute_zscore
from .capture import take_screenshot
from .ui import (
    ClickWindow,
    destroy_root,
    run_in_tk,
    show_error,
    show_result,
    tk_mainloop,
)

# ---------------------------------------------------------------------------
# Measurement workflow
# ---------------------------------------------------------------------------


def _on_clicks_done(clicks) -> None:
    """Handle the result of the ClickWindow – runs on the Tkinter main thread."""
    if clicks is None:
        return
    try:
        (_, y_mean), (_, y_plus1sd), (_, y_minus1sd), (_, y_point) = clicks
        z = compute_zscore(y_mean, y_plus1sd, y_minus1sd, y_point)
        show_result(z)
    except ValueError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Unerwarteter Fehler:\n{e}")


def start_measurement() -> None:
    """Take a screenshot in a background thread, then open the ClickWindow."""
    def _worker():
        try:
            img = take_screenshot()
        except Exception as e:
            run_in_tk(lambda: show_error(f"Screenshot fehlgeschlagen:\n{e}"))
            return
        run_in_tk(lambda: ClickWindow(img, _on_clicks_done))

    threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Tray icon
# ---------------------------------------------------------------------------

def _create_tray_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (26, 26, 46, 255))
    draw = ImageDraw.Draw(img)
    m = 10
    draw.line([(m, m), (size - m, m)], fill="#00bfff", width=5)
    draw.line([(size - m, m), (m, size - m)], fill="#00bfff", width=5)
    draw.line([(m, size - m), (size - m, size - m)], fill="#00bfff", width=5)
    return img


def _on_measure(icon, item) -> None:
    run_in_tk(start_measurement)


def _on_quit(icon, item) -> None:
    icon.stop()
    destroy_root()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Tkinter runs on a dedicated non-daemon thread so the process stays alive
    tk_thread = threading.Thread(target=tk_mainloop, daemon=False)
    tk_thread.start()

    icon_image = _create_tray_icon()
    menu = pystray.Menu(
        pystray.MenuItem("📐 Z-Score messen", _on_measure, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Beenden", _on_quit),
    )
    tray = pystray.Icon("ZScoreToolbox", icon_image, "Z-Score Toolbox", menu)
    tray.run()


if __name__ == "__main__":
    main()
