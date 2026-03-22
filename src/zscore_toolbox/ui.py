"""Tkinter UI components: thread-safe queue, ClickWindow, result/error popups."""

import queue
import tkinter as tk
from PIL import Image, ImageTk

# ---------------------------------------------------------------------------
# Thread-safe Tkinter dispatch
# ---------------------------------------------------------------------------

_tk_queue: queue.Queue = queue.Queue()
_root: tk.Tk | None = None


def run_in_tk(fn) -> None:
    """Schedule *fn* to run on the Tkinter main thread."""
    _tk_queue.put(fn)


def tk_mainloop() -> None:
    """Create the hidden root window and start the Tkinter event loop.

    Must be called from the thread that will own all Tkinter widgets.
    """
    global _root
    _root = tk.Tk()
    _root.withdraw()

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


def destroy_root() -> None:
    """Destroy the root window after a short delay (called from any thread)."""
    if _root:
        _root.after(100, _root.destroy)


# ---------------------------------------------------------------------------
# Click labels
# ---------------------------------------------------------------------------

LABELS = [
    ("Mean",      "#00bfff"),
    ("+1 SD",     "#00e676"),
    ("-1 SD",     "#ff5252"),
    ("Messpunkt", "#ffd740"),
]

# ---------------------------------------------------------------------------
# Interactive click window
# ---------------------------------------------------------------------------


class ClickWindow:
    """Full-screen overlay that collects four clicks from the user."""

    def __init__(self, image: Image.Image, done_callback):
        self.image = image
        self.done_callback = done_callback
        self.clicks: list[tuple[int, int]] = []
        self._tk_image = None  # keep reference so GC won't collect it

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

        self._tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_image)

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


# ---------------------------------------------------------------------------
# Result and error popups
# ---------------------------------------------------------------------------

def _center_popup(popup: tk.Toplevel) -> None:
    popup.update_idletasks()
    w, h = popup.winfo_width(), popup.winfo_height()
    sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
    popup.geometry(f"+{(sw - w)//2}+{(sh - h)//2}")


def show_result(z: float) -> None:
    """Display the calculated Z-score in a centered popup."""
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

    _center_popup(popup)


def show_error(msg: str) -> None:
    """Display an error message in a centered popup."""
    popup = tk.Toplevel(_root)
    popup.title("Fehler")
    popup.configure(bg="#1a1a2e")
    popup.attributes("-topmost", True)
    tk.Label(popup, text=msg, bg="#1a1a2e", fg="#ff5252",
             font=("Segoe UI", 11), padx=20, pady=20, wraplength=350).pack()
    tk.Button(popup, text="OK", command=popup.destroy,
              bg="#3d3d6b", fg="white", font=("Segoe UI", 10),
              relief="flat", padx=20, pady=6).pack(pady=(0, 16))
    _center_popup(popup)
