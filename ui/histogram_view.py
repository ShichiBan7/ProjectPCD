"""Grafik histogram dengan sumbu, garis bantu, penanda rata-rata, dan hover."""
import math
import numpy as np
from tkinter import Canvas
from config import C_CANVAS, C_ACCENT, C_MUTED, C_TITLE_CARD, FONT

KIRI, KANAN, ATAS, BAWAH = 66, 16, 12, 42
TICK_X = [0, 32, 64, 96, 128, 160, 192, 224, 255]
WARNA_GRID = "#e2e8f0"
WARNA_RATA = "#ef4444"


def format_angka(n):
    """12500 -> '12.500' (pemisah ribuan gaya Indonesia)."""
    return f"{int(round(n)):,}".replace(",", ".")


def format_desimal(x, digit=1):
    return f"{x:.{digit}f}".replace(".", ",")


def tick_linear(maks, jumlah=4):
    """Tick sumbu Y dengan angka 'bulat' (1, 2, 5 x 10^n). Mengembalikan (daftar_tick, batas_atas)."""
    if maks <= 0:
        return [0, 1], 1
    kasar = maks / jumlah
    mag = 10 ** math.floor(math.log10(kasar))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= kasar)
    step = max(math.ceil(step), 1)   # sumbu jumlah piksel selalu berupa bilangan bulat
    atas = math.ceil(maks / step) * step
    return [i * step for i in range(int(round(atas / step)) + 1)], atas


class HistogramView(Canvas):
    def __init__(self, parent, height=210):
        super().__init__(parent, height=height, bg=C_CANVAS, highlightthickness=0)
        self.data = None
        self.rata = None
        self.bind("<Configure>", lambda e: self.gambar())
        self.bind("<Motion>", self.on_hover)
        self.bind("<Leave>", lambda e: self.delete("hover"))

    # ---------------- antarmuka ----------------
    def tampilkan(self, data, rata=None):
        """data = 256 angka (atau None); rata = rata-rata kecerahan untuk garis penanda."""
        self.data = None if data is None else np.asarray(data, dtype=np.float64)
        self.rata = rata
        self.gambar()

    # ---------------- koordinat ----------------
    def _area(self):
        w, h = max(self.winfo_width(), 200), max(self.winfo_height(), 120)
        return w, h, KIRI, ATAS, w - KANAN, h - BAWAH   # w, h, x0, y0, x1, y1

    def _x(self, nilai, x0, x1):
        return x0 + (nilai + 0.5) / 256.0 * (x1 - x0)

    def _y(self, hitung, y0, y1):
        """Mengubah jumlah piksel menjadi koordinat y."""
        if hitung <= 0:
            return y1
        return y1 - min(max(hitung / self._atas, 0), 1) * (y1 - y0)

    # ---------------- menggambar ----------------
    def gambar(self):
        self.delete("all")
        w, h, x0, y0, x1, y1 = self._area()
        if self.data is None:
            self.create_text(w // 2, h // 2, text="[ Histogram ]", fill=C_MUTED, font=(FONT, 9))
            return

        maks = float(self.data.max())
        ticks_y, self._atas = tick_linear(maks)

        # garis bantu & label sumbu Y
        for t in ticks_y:
            y = self._y(t, y0, y1)
            self.create_line(x0, y, x1, y, fill=WARNA_GRID)
            self.create_text(x0 - 6, y, text=format_angka(t), anchor="e", fill=C_TITLE_CARD, font=(FONT, 7))
        # garis bantu & label sumbu X
        for t in TICK_X:
            x = self._x(t, x0, x1)
            self.create_line(x, y0, x, y1, fill=WARNA_GRID)
            self.create_text(x, y1 + 5, text=str(t), anchor="n", fill=C_TITLE_CARD, font=(FONT, 7))

        # batang histogram (satu batang per tingkat kecerahan)
        lebar = (x1 - x0) / 256.0
        for i, c in enumerate(self.data):
            if c > 0:
                xa = x0 + i * lebar
                self.create_rectangle(xa, self._y(c, y0, y1), xa + max(lebar, 1), y1,
                                      fill=C_ACCENT, outline="")

        # sumbu
        self.create_line(x0, y0, x0, y1, fill=C_TITLE_CARD)
        self.create_line(x0, y1, x1, y1, fill=C_TITLE_CARD)
        self.create_text(12, (y0 + y1) / 2, text="Jumlah piksel", angle=90, fill=C_TITLE_CARD, font=(FONT, 8, "bold"))
        self.create_text((x0 + x1) / 2, h - 4, text="Tingkat kecerahan (0 = hitam, 255 = putih)",
                         anchor="s", fill=C_TITLE_CARD, font=(FONT, 8, "bold"))

        # penanda rata-rata
        if self.rata is not None:
            xr = x0 + self.rata / 256.0 * (x1 - x0)
            self.create_line(xr, y0, xr, y1, fill=WARNA_RATA, dash=(4, 3), width=1)
            kanan = xr > (x0 + x1) / 2
            self.create_text(xr + (-4 if kanan else 4), y0 + 2, anchor="ne" if kanan else "nw",
                             text=f"rata-rata {format_desimal(self.rata)}", fill=WARNA_RATA, font=(FONT, 7, "bold"))

    # ---------------- hover ----------------
    def on_hover(self, e):
        self.delete("hover")
        if self.data is None:
            return
        w, h, x0, y0, x1, y1 = self._area()
        if not (x0 <= e.x <= x1):
            return
        i = min(max(int((e.x - x0) / (x1 - x0) * 256), 0), 255)
        c = self.data[i]
        total = self.data.sum()
        persen = c / total * 100 if total else 0
        x = self._x(i, x0, x1)
        self.create_line(x, y0, x, y1, fill=C_TITLE_CARD, tags="hover")
        self.create_oval(x - 3, self._y(c, y0, y1) - 3, x + 3, self._y(c, y0, y1) + 3,
                         fill=C_TITLE_CARD, outline="white", tags="hover")
        teks = f"Nilai {i}  |  {format_angka(c)} piksel  ({format_desimal(persen, 2)}%)"
        t = self.create_text(0, 0, text=teks, anchor="nw", font=(FONT, 8, "bold"), fill="white", tags="hover")
        bx0, by0, bx1, by1 = self.bbox(t)
        lebar_t, tinggi_t = bx1 - bx0, by1 - by0
        px = x + 10 if x + 10 + lebar_t + 8 < w else x - 10 - lebar_t - 8
        py = y0 + 18
        self.coords(t, px + 4, py + 2)
        kotak = self.create_rectangle(px, py, px + lebar_t + 8, py + tinggi_t + 4,
                                      fill=C_TITLE_CARD, outline="", tags="hover")
        self.tag_lower(kotak, t)
