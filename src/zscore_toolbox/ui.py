"""Tkinter UI components: thread-safe queue, ClickWindow, result/error popups."""

import queue
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance

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
# Step definitions
# ---------------------------------------------------------------------------

STEPS = [
    ("Mean",    "#00bfff", "Click the MEAN line"),
    ("+1 SD",   "#00e676", "Click the +1 SD line"),
    ("-1 SD",   "#ff5252", "Click the -1 SD line"),
    ("Point",   "#ffd740", "Click the measurement POINT"),
]

# ---------------------------------------------------------------------------
# Interactive click window (full UX overhaul)
# ---------------------------------------------------------------------------


class ClickWindow:
    """Full-screen overlay that collects four clicks from the user."""

    PANEL_WIDTH = 260

    def __init__(self, image: Image.Image, done_callback):
        self.image = image
        self.done_callback = done_callback
        self.clicks: list[tuple[int, int]] = []
        self._tk_image = None
        self._h_line_id = None  # horizontal crosshair line
        self._coord_id = None   # coordinate label next to cursor

        self.win = tk.Toplevel(_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.win.title("Z-Score Toolbox")

        # --- Main canvas with darkened screenshot ---
        darkened = ImageEnhance.Brightness(image).enhance(0.35)
        self._tk_image = ImageTk.PhotoImage(darkened)

        self.canvas = tk.Canvas(
            self.win,
            width=image.width,
            height=image.height,
            highlightthickness=0,
            cursor="none",
            bg="black",
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_image)

        # --- Left-side step panel ---
        self._build_step_panel()

        # --- ESC hint at bottom center ---
        self.canvas.create_text(
            image.width // 2, image.height - 30,
            text="Press ESC to cancel",
            fill="#888888", font=("Segoe UI", 12),
            anchor="s",
        )

        # --- Bindings ---
        self.win.bind("<Escape>", lambda _: self._cancel())
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)

    # ----- step panel -----

    def _build_step_panel(self):
        """Draw the step-by-step instruction panel on the left side."""
        px = 20   # left padding
        py = 60   # top start
        lh = 52   # line height per step

        # Panel background
        self.canvas.create_rectangle(
            0, 0, self.PANEL_WIDTH, py + len(STEPS) * lh + 30,
            fill="#111122", outline="", stipple="",
        )
        # Semi-transparent effect via a darker rectangle
        self.canvas.create_rectangle(
            0, 0, self.PANEL_WIDTH, py + len(STEPS) * lh + 30,
            fill="#0a0a18", outline="",
        )

        self.canvas.create_text(
            px, 24, text="MEASUREMENT STEPS",
            fill="#aaaacc", font=("Segoe UI", 11, "bold"), anchor="nw",
        )

        self._step_markers = []
        self._step_labels = []
        self._step_checks = []
        for i, (name, color, instruction) in enumerate(STEPS):
            y = py + i * lh

            # Marker (circle indicator)
            marker = self.canvas.create_oval(
                px, y + 6, px + 16, y + 22,
                outline=color, width=2, fill="",
            )
            self._step_markers.append(marker)

            # Step label text
            label = self.canvas.create_text(
                px + 24, y + 4,
                text=f"Step {i+1}: {name}",
                fill="#666688", font=("Segoe UI", 11, "bold"), anchor="nw",
            )
            self._step_labels.append(label)

            # Instruction text
            instr = self.canvas.create_text(
                px + 24, y + 24,
                text=instruction,
                fill="#555577", font=("Segoe UI", 9), anchor="nw",
            )
            self._step_labels.append(instr)

            # Checkmark (hidden initially)
            check = self.canvas.create_text(
                px + 5, y + 7,
                text="\u2713", fill=color,
                font=("Segoe UI", 14, "bold"), anchor="nw",
                state="hidden",
            )
            self._step_checks.append(check)

        self._highlight_step(0)

    def _highlight_step(self, idx: int):
        """Highlight the current step and dim others."""
        for i, (name, color, instruction) in enumerate(STEPS):
            if i == idx:
                self.canvas.itemconfig(self._step_labels[i * 2], fill=color,
                                       font=("Segoe UI", 11, "bold"))
                self.canvas.itemconfig(self._step_labels[i * 2 + 1], fill="#aaaacc")
                self.canvas.itemconfig(self._step_markers[i], width=3)
            elif i < idx:
                # Completed — dimmed with check
                self.canvas.itemconfig(self._step_labels[i * 2], fill="#666688")
                self.canvas.itemconfig(self._step_labels[i * 2 + 1], fill="#555577")
            else:
                # Future
                self.canvas.itemconfig(self._step_labels[i * 2], fill="#444466")
                self.canvas.itemconfig(self._step_labels[i * 2 + 1], fill="#333355")

        # Update header with current step number
        if idx < len(STEPS):
            name, color, _ = STEPS[idx]
            self._ensure_header(idx, name, color)

    def _ensure_header(self, idx, name, color):
        """Show 'Step N/4 — description' at top of panel."""
        tag = "step_header"
        self.canvas.delete(tag)
        self.canvas.create_text(
            self.PANEL_WIDTH // 2, self.image.height - 70,
            text=f"Step {idx+1}/4 — {name}",
            fill=color, font=("Segoe UI", 13, "bold"),
            anchor="s", tags=tag,
        )

    # ----- mouse interaction -----

    def _on_motion(self, event):
        """Draw a full-width horizontal crosshair and show Y-coordinate."""
        x, y = event.x, event.y

        # Delete previous crosshair and coord label
        if self._h_line_id:
            self.canvas.delete(self._h_line_id)
        if self._coord_id:
            self.canvas.delete(self._coord_id)

        idx = len(self.clicks)
        color = STEPS[idx][1] if idx < len(STEPS) else "#ffffff"

        # Full-width horizontal line
        self._h_line_id = self.canvas.create_line(
            0, y, self.image.width, y,
            fill=color, width=1, dash=(6, 4),
        )

        # Y-coordinate label next to cursor
        self._coord_id = self.canvas.create_text(
            x + 20, y - 12,
            text=f"Y: {y}",
            fill=color, font=("Segoe UI", 10, "bold"), anchor="w",
        )

    def _on_click(self, event):
        idx = len(self.clicks)
        if idx >= len(STEPS):
            return

        x, y = event.x, event.y
        self.clicks.append((x, y))

        name, color, _ = STEPS[idx]

        # Draw permanent full-width horizontal line at click position
        self.canvas.create_line(
            0, y, self.image.width, y,
            fill=color, width=2,
        )

        # Label on the right side of the line
        self.canvas.create_text(
            self.image.width - 15, y - 10,
            text=f"{name}  (Y={y})",
            fill=color, font=("Segoe UI", 10, "bold"), anchor="e",
        )

        # Small crosshair marker at click point
        r = 8
        self.canvas.create_line(x - r, y, x + r, y, fill=color, width=2)
        self.canvas.create_line(x, y - r, x, y + r, fill=color, width=2)

        # Update step panel: show check, highlight next
        self.canvas.itemconfig(self._step_checks[idx], state="normal")
        self.canvas.itemconfig(self._step_markers[idx], state="hidden")

        if len(self.clicks) == len(STEPS):
            # Remove crosshair line and coord
            if self._h_line_id:
                self.canvas.delete(self._h_line_id)
                self._h_line_id = None
            if self._coord_id:
                self.canvas.delete(self._coord_id)
                self._coord_id = None
            self.canvas.delete("step_header")
            self.win.after(400, self._finish)
        else:
            self._highlight_step(idx + 1)

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


def show_result(z: float, measure_again_callback=None) -> None:
    """Display the calculated Z-score in a centered popup with gauge and actions."""
    popup = tk.Toplevel(_root)
    popup.title("Z-Score Result")
    popup.configure(bg="#1a1a2e")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    if z > 0:
        direction, color = "above the Mean", "#00e676"
    elif z < 0:
        direction, color = "below the Mean", "#ff5252"
    else:
        direction, color = "at the Mean", "#00bfff"

    arrow = "\u2191" if z > 0 else ("\u2193" if z < 0 else "=")

    # Header
    tk.Label(popup, text="Z-Score", bg="#1a1a2e", fg="#aaaacc",
             font=("Segoe UI", 11)).pack(pady=(18, 2))

    # Large Z value
    tk.Label(popup, text=f"{z:+.3f}", bg="#1a1a2e", fg=color,
             font=("Segoe UI", 36, "bold")).pack(padx=40)

    # Direction label
    tk.Label(popup, text=f"{arrow} {direction}", bg="#1a1a2e", fg="#cccccc",
             font=("Segoe UI", 10)).pack(pady=(2, 10))

    # --- Visual gauge bar (-3 to +3) ---
    gauge_frame = tk.Frame(popup, bg="#1a1a2e")
    gauge_frame.pack(padx=20, pady=(0, 10))

    gauge_w, gauge_h = 280, 24
    gauge = tk.Canvas(gauge_frame, width=gauge_w, height=gauge_h,
                      bg="#1a1a2e", highlightthickness=0)
    gauge.pack()

    # Gauge track
    track_y = gauge_h // 2
    gauge.create_line(10, track_y, gauge_w - 10, track_y, fill="#333355", width=4)

    # Tick marks at -3, -2, -1, 0, 1, 2, 3
    usable = gauge_w - 20
    for tick in range(-3, 4):
        tx = 10 + (tick + 3) / 6 * usable
        tick_color = "#666688" if tick != 0 else "#aaaacc"
        gauge.create_line(tx, track_y - 6, tx, track_y + 6, fill=tick_color, width=1)
        gauge.create_text(tx, track_y + 12, text=str(tick), fill="#666688",
                          font=("Segoe UI", 7), anchor="n")

    # Marker position (clamp to -3..+3 range for display)
    clamped = max(-3.0, min(3.0, z))
    mx = 10 + (clamped + 3) / 6 * usable
    gauge.create_oval(mx - 6, track_y - 6, mx + 6, track_y + 6,
                      fill=color, outline="white", width=1)

    # --- Button row ---
    btn_frame = tk.Frame(popup, bg="#1a1a2e")
    btn_frame.pack(pady=(4, 16))

    btn_style = dict(
        bg="#3d3d6b", fg="white", font=("Segoe UI", 10),
        relief="flat", padx=12, pady=6, cursor="hand2",
    )

    def _copy():
        popup.clipboard_clear()
        popup.clipboard_append(f"{z:+.3f}")

    tk.Button(btn_frame, text="Copy", command=_copy, **btn_style).pack(
        side="left", padx=4)

    if measure_again_callback:
        def _again():
            popup.destroy()
            measure_again_callback()

        tk.Button(btn_frame, text="Measure again", command=_again,
                  **btn_style).pack(side="left", padx=4)

    tk.Button(btn_frame, text="OK", command=popup.destroy,
              **btn_style).pack(side="left", padx=4)

    _center_popup(popup)


def show_error(msg: str) -> None:
    """Display an error message in a centered popup."""
    popup = tk.Toplevel(_root)
    popup.title("Error")
    popup.configure(bg="#1a1a2e")
    popup.attributes("-topmost", True)
    tk.Label(popup, text=msg, bg="#1a1a2e", fg="#ff5252",
             font=("Segoe UI", 11), padx=20, pady=20, wraplength=350).pack()
    tk.Button(popup, text="OK", command=popup.destroy,
              bg="#3d3d6b", fg="white", font=("Segoe UI", 10),
              relief="flat", padx=20, pady=6).pack(pady=(0, 16))
    _center_popup(popup)
