"""Komponen tampilan kecil yang dipakai ulang."""
from tkinter import Canvas, Label
from config import C_WIN, C_ACCENT, C_BTN, C_BTN_HOVER, C_TEXT, FONT


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class FlatSlider(Canvas):
    def __init__(self, parent, from_, to, variable, bg=C_WIN):
        super().__init__(parent, height=26, bg=bg, highlightthickness=0, cursor="hand2")
        self.from_, self.to, self.var, self.pad = from_, to, variable, 12
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Button-1>", self.on_move)
        self.bind("<B1-Motion>", self.on_move)
        self.var.trace_add("write", lambda *a: self.redraw())

    def set_range(self, from_, to):
        """Mengubah rentang slider sesuai operasi yang dipilih."""
        self.from_, self.to = from_, to
        self.redraw()

    def on_move(self, e):
        w = max(self.winfo_width() - 2 * self.pad, 1)
        frac = min(max((e.x - self.pad) / w, 0), 1)
        self.var.set(round(self.from_ + frac * (self.to - self.from_)))

    def redraw(self):
        self.delete("all")
        w, cy = self.winfo_width(), 13
        span = max(w - 2 * self.pad, 1)
        rentang = max(self.to - self.from_, 1)
        frac = min(max((self.var.get() - self.from_) / rentang, 0), 1)
        x = self.pad + frac * span

        # Garis dasar penuh
        self.create_line(self.pad, cy, w - self.pad, cy, fill="#d4d4d4", width=3)

        # Jika rentang mencakup nilai negatif dan positif, tarik garis aksen dari titik 0
        if self.from_ < 0 < self.to:
            x_zero = self.pad + (0 - self.from_) / rentang * span
            self.create_line(x_zero, cy - 5, x_zero, cy + 5, fill="#94a3b8", width=1)
            self.create_line(x_zero, cy, x, cy, fill=C_ACCENT, width=3)
        else:
            self.create_line(self.pad, cy, x, cy, fill=C_ACCENT, width=3)

        self.create_oval(x - 9, cy - 9, x + 9, cy + 9, fill="white", outline="#d9d9d9")


class FlatButton(Label):
    def __init__(self, parent, text, command, bg=C_BTN, hover=C_BTN_HOVER, fg=C_TEXT):
        super().__init__(parent, text=text, bg=bg, fg=fg, padx=14, pady=6,
                         font=(FONT, 8, "bold"), cursor="hand2")
        self.bg, self.hover = bg, hover
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", lambda e: self.config(bg=self.hover))
        self.bind("<Leave>", lambda e: self.config(bg=self.bg))
