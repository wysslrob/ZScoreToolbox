"""Entry point: system tray icon and measurement workflow."""

import threading

from PIL import Image, ImageDraw
import pystray

from zscore_toolbox.calculator import compute_zscore
from zscore_toolbox.capture import take_screenshot
from zscore_toolbox.ui import (
    ClickWindow,
    destroy_root,
    run_in_tk,
    show_error,
    show_result,
    tk_mainloop,
)

# ---------------------------------------------------------------------------
# Global state for tray menu updates
# ---------------------------------------------------------------------------

_tray: pystray.Icon | None = None
_last_result: str = "—"


def _rebuild_menu() -> None:
    """Rebuild the tray menu to reflect updated state."""
    if _tray is None:
        return
    _tray.menu = pystray.Menu(
        pystray.MenuItem("Measure Z-Score", _on_measure, default=True),
        pystray.MenuItem(f"Last result: {_last_result}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _on_quit),
    )
    _tray.update_menu()


# ---------------------------------------------------------------------------
# Measurement workflow
# ---------------------------------------------------------------------------


def _on_clicks_done(clicks) -> None:
    """Handle the result of the ClickWindow — runs on the Tkinter main thread."""
    global _last_result
    if clicks is None:
        return
    try:
        (_, y_mean), (_, y_plus1sd), (_, y_minus1sd), (_, y_point) = clicks
        z = compute_zscore(y_mean, y_plus1sd, y_minus1sd, y_point)
        _last_result = f"{z:+.3f}"
        _rebuild_menu()
        show_result(z, measure_again_callback=lambda: run_in_tk(start_measurement))
    except ValueError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Unexpected error:\n{e}")


def start_measurement() -> None:
    """Take a screenshot in a background thread, then open the ClickWindow."""
    def _worker():
        try:
            img = take_screenshot()
        except Exception as e:
            run_in_tk(lambda: show_error(f"Screenshot failed:\n{e}"))
            return
        run_in_tk(lambda: ClickWindow(img, _on_clicks_done))

    threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Tray icon
# ---------------------------------------------------------------------------

def _create_tray_icon() -> Image.Image:
    """Create a small icon image for the system tray."""
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
    global _tray

    # Tkinter runs on a dedicated non-daemon thread so the process stays alive
    tk_thread = threading.Thread(target=tk_mainloop, daemon=False)
    tk_thread.start()

    icon_image = _create_tray_icon()
    menu = pystray.Menu(
        pystray.MenuItem("Measure Z-Score", _on_measure, default=True),
        pystray.MenuItem(f"Last result: {_last_result}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _on_quit),
    )
    _tray = pystray.Icon(
        "ZScoreToolbox",
        icon_image,
        "ZScore Toolbox — Click to measure",
        menu,
    )
    _tray.run()


if __name__ == "__main__":
    main()
