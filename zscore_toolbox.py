"""
Z-Score Toolbox
===============
System-Tray Tool für Windows.
- Klick auf Tray-Icon → Screenshot → 4 Klicks (Mean, +1SD, -1SD, Messpunkt)
- Ausgabe: Z-Score als Popup

Installation:
    python -m pip install pystray pillow mss
"""

import threading
import queue
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import mss
import pystray

# Alle Tkinter-Operationen laufen über diese Queue im Haupt-Thread
_tk_queue: queue.Queue = queue.Queue()
_root: tk.Tk | None = None


# ──────────────────────────────────────────────
# Haupt-Thread Tkinter-Schleife
# ──────────────────────────────────────────────

def _tk_mainloop():
    """Läuft im Haupt-Thread. Verarbeitet Tkinter-Jobs aus der Queue."""
    global _root
    _root = tk.Tk()
    _root.withdraw()  # Haupt-Fenster unsichtbar

    def _poll():
        try:
            while True:
                fn = _tk_queue.get_nowait()
                fn()
        except queue.Empty:
            pass
        _root.after(50, _poll)

    _root.after(50, _poll)
    _root.mainloop()


def run_in_tk(fn):
    """Schickt eine Funktion in den Haupt-Thread zur Ausführung."""
    _tk_queue.put(fn)


# ──────────────────────────────────────────────
# Screenshot
# ──────────────────────────────────────────────

def take_screenshot() -> Image.Image:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


# ──────────────────────────────────────────────
# Interaktives Klick-Fenster
# ──────────────────────────────────────────────

LABELS = [
    ("Mean",      "#00bfff"),
    ("+1 SD",     "#00e676"),
    ("-1 SD",     "#ff5252"),
    ("Messpunkt", "#ffd740"),
]


class ClickWindow:
    def __init__(self, image: Image.Image, done_callback):
        self.image = image
        self.done_callback = done_callback
        self.clicks: list[tuple[int, int]] = []
        self._tk_image = None  # Referenz halten damit GC es nicht löscht

        self.win = tk.Toplevel(_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.win.title("Z-Score Toolbox")

        self.canvas = tk.Canvas(
            self.win,
            width=image.width,
            height=image.height,
            highlightthickness=0,
            cursor="crosshair",
            bg="black",
        )
        self.canvas.pack(fill="both", expand=True)

        # Bild laden im gleichen Thread wie Canvas
        self._tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_image)

        # Info-Label
        self.info_var = tk.StringVar()
        self._update_info()
        tk.Label(
            self.win,
            textvariable=self.info_var,
            bg="#1a1a2e", fg="white",
            font=("Segoe UI", 13, "bold"),
            padx=12, pady=6,
        ).place(relx=0.5, rely=0.0, anchor="n")

        self.win.bind("<Escape>", lambda _: self._cancel())
        self.canvas.bind("<Button-1>", self._on_click)

    def _update_info(self):
        idx = len(self.clicks)
        if idx < len(LABELS):
            label, _ = LABELS[idx]
            self.info_var.set(f"Klick {idx+1}/4 → {label}    |    ESC = Abbrechen")

    def _on_click(self, event):
        idx = len(self.clicks)
        if idx >= len(LABELS):
            return

        x, y = event.x, event.y
        self.clicks.append((x, y))

        label, color = LABELS[idx]
        r = 10
        self.canvas.create_line(x - r, y, x + r, y, fill=color, width=2)
        self.canvas.create_line(x, y - r, x, y + r, fill=color, width=2)
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
        self.canvas.create_text(x + 15, y, text=label, fill=color, anchor="w",
                                font=("Segoe UI", 11, "bold"))

        if len(self.clicks) == len(LABELS):
            self.win.after(300, self._finish)
        else:
            self._update_info()

    def _finish(self):
        result = list(self.clicks)
        self.win.destroy()
        self.done_callback(result)

    def _cancel(self):
        self.win.destroy()
        self.done_callback(None)


# ──────────────────────────────────────────────
# Ergebnis-Popup
# ──────────────────────────────────────────────

def show_result(z: float):
    popup = tk.Toplevel(_root)
    popup.title("Z-Score")
    popup.configure(bg="#1a1a2e")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    if z > 0:
        direction, color = "↑ über dem Mean", "#00e676"
    elif z < 0:
        direction, color = "↓ unter dem Mean", "#ff5252"
    else:
        direction, color = "= Mean", "#00bfff"

    tk.Label(popup, text="Z-Score", bg="#1a1a2e", fg="#aaaacc",
             font=("Segoe UI", 11)).pack(pady=(18, 2))
    tk.Label(popup, text=f"{z:+.3f}", bg="#1a1a2e", fg=color,
             font=("Segoe UI", 36, "bold")).pack(padx=40)
    tk.Label(popup, text=direction, bg="#1a1a2e", fg="#cccccc",
             font=("Segoe UI", 10)).pack(pady=(2, 14))
    tk.Button(popup, text="OK", command=popup.destroy,
              bg="#3d3d6b", fg="white", font=("Segoe UI", 10),
              relief="flat", padx=20, pady=6, cursor="hand2").pack(pady=(0, 16))

    popup.update_idletasks()
    w, h = popup.winfo_width(), popup.winfo_height()
    sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
    popup.geometry(f"+{(sw - w)//2}+{(sh - h)//2}")


def show_error(msg: str):
    popup = tk.Toplevel(_root)
    popup.title("Fehler")
    popup.configure(bg="#1a1a2e")
    popup.attributes("-topmost", True)
    tk.Label(popup, text=msg, bg="#1a1a2e", fg="#ff5252",
             font=("Segoe UI", 11), padx=20, pady=20, wraplength=350).pack()
    tk.Button(popup, text="OK", command=popup.destroy,
              bg="#3d3d6b", fg="white", font=("Segoe UI", 10),
              relief="flat", padx=20, pady=6).pack(pady=(0, 16))
    popup.update_idletasks()
    w, h = popup.winfo_width(), popup.winfo_height()
    sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
    popup.geometry(f"+{(sw - w)//2}+{(sh - h)//2}")


# ──────────────────────────────────────────────
# Z-Score Berechnung
# ──────────────────────────────────────────────

def compute_zscore(y_mean, y_plus1sd, y_minus1sd, y_point) -> float:
    sd_pixels = ((y_mean - y_plus1sd) + (y_minus1sd - y_mean)) / 2
    if abs(sd_pixels) < 0.5:
        raise ValueError(
            "Mean und ±1 SD liegen zu nah beieinander.\n"
            "Bitte die Punkte weiter auseinander markieren."
        )
    return round((y_mean - y_point) / sd_pixels, 3)


# ──────────────────────────────────────────────
# Workflow
# ──────────────────────────────────────────────

def _on_clicks_done(clicks):
    """Callback nach dem Klick-Fenster – läuft im Haupt-Thread."""
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


def start_measurement():
    """Screenshot im Hintergrund, dann Fenster im Haupt-Thread."""
    def _worker():
        try:
            img = take_screenshot()
        except Exception as e:
            run_in_tk(lambda: show_error(f"Screenshot fehlgeschlagen:\n{e}"))
            return
        run_in_tk(lambda: ClickWindow(img, _on_clicks_done))

    threading.Thread(target=_worker, daemon=True).start()


# ──────────────────────────────────────────────
# Tray-Icon
# ──────────────────────────────────────────────

def create_tray_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (26, 26, 46, 255))
    draw = ImageDraw.Draw(img)
    m = 10
    draw.line([(m, m), (size - m, m)], fill="#00bfff", width=5)
    draw.line([(size - m, m), (m, size - m)], fill="#00bfff", width=5)
    draw.line([(m, size - m), (size - m, size - m)], fill="#00bfff", width=5)
    return img


def on_measure(icon, item):
    run_in_tk(start_measurement)


def on_quit(icon, item):
    icon.stop()
    if _root:
        _root.after(100, _root.destroy)


def main():
    # Tkinter läuft in eigenem Thread
    tk_thread = threading.Thread(target=_tk_mainloop, daemon=False)
    tk_thread.start()

    # Tray-Icon (blockiert bis Beenden)
    icon_image = create_tray_icon()
    menu = pystray.Menu(
        pystray.MenuItem("📐 Z-Score messen", on_measure, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Beenden", on_quit),
    )
    tray = pystray.Icon("ZScoreToolbox", icon_image, "Z-Score Toolbox", menu)
    tray.run()


if __name__ == "__main__":
    main()
