from tkinter import Toplevel, Frame, Label, Canvas, Scrollbar, BOTH, X, Y, LEFT, RIGHT
from config import C_WIN, C_CARD, C_TITLE_CARD, C_TEXT, FONT
from processing.histogram import statistik_histogram, kesimpulan
from ui.histogram_view import HistogramView, format_angka, format_desimal


class HistogramWindow(Toplevel):
    def __init__(self, parent, saat_ditutup):
        super().__init__(parent)
        self.saat_ditutup = saat_ditutup
        self.title("Detail Analisis Histogram")
        self.geometry("800x760")
        self.minsize(560, 480)
        self.configure(bg=C_WIN)
        self._wheel_acc = 0

        # ---- Scrollbar & Canvas Utama ----
        self.outer_canvas = Canvas(self, bg=C_WIN, highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.outer_canvas.yview)
        self.outer_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.outer_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.inner = Frame(self.outer_canvas, bg=C_WIN)
        self.win_id = self.outer_canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._update_scrollregion)
        self.outer_canvas.bind("<Configure>", self._on_canvas_resize)

        # ---- Petunjuk singkat ----
        atas = Frame(self.inner, bg=C_WIN)
        atas.pack(fill=X, padx=14, pady=(10, 0))
        Label(
            atas,
            text="Tips: Gunakan scrollbar kanan, tombol panah Atas/Bawah, atau klik-tahan & geser area abu-abu untuk menggulir.",
            bg=C_WIN, fg="#64748b", font=(FONT, 8)
        ).pack(side=LEFT)

        self.cards, self.grafik, self.info = {}, {}, {}
        spek = (
            ("asli", "HISTOGRAM CITRA ASLI"),
            ("kedua", "HISTOGRAM CITRA KEDUA"),
            ("hasil", "HISTOGRAM CITRA HASIL"),
        )
        for kunci, judul in spek:
            card = Frame(
                self.inner, bg=C_CARD, padx=12, pady=10,
                highlightthickness=1, highlightbackground="#e2e8f0"
            )
            Label(card, text=judul, bg=C_CARD, fg=C_TITLE_CARD, font=(FONT, 9, "bold")).pack(pady=(0, 6))
            grafik = HistogramView(card, height=195)
            grafik.pack(fill=BOTH, expand=True)
            info = Label(card, text="", bg=C_CARD, fg=C_TEXT, font=(FONT, 8), justify=LEFT, anchor="w")
            info.pack(fill=X, pady=(8, 0))
            self.cards[kunci], self.grafik[kunci], self.info[kunci] = card, grafik, info

        self.cards["asli"].pack(fill=X, padx=14, pady=(8, 6))
        self.cards["hasil"].pack(fill=X, padx=14, pady=(4, 14))

        # Pasang semua metode scroll (Wheel/Touchpad, Keyboard, & Drag-to-Scroll)
        self._pasang_navigasi_scroll(self)

        self.protocol("WM_DELETE_WINDOW", self.tutup)
        self.bind("<Escape>", lambda e: self.tutup())
        self.after(50, self.focus_force)

    def _pasang_navigasi_scroll(self, widget):
        # 1. Mouse wheel & touchpad yang mengirim WM_MOUSEWHEEL
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", lambda e: self.outer_canvas.yview_scroll(-2, "units"), add="+")
        widget.bind("<Button-5>", lambda e: self.outer_canvas.yview_scroll(2, "units"), add="+")

        # 2. Navigasi Keyboard (Panah Atas/Bawah, PageUp/PageDown)
        widget.bind("<Up>", lambda e: self.outer_canvas.yview_scroll(-2, "units"), add="+")
        widget.bind("<Down>", lambda e: self.outer_canvas.yview_scroll(2, "units"), add="+")
        widget.bind("<Prior>", lambda e: self.outer_canvas.yview_scroll(-1, "pages"), add="+")
        widget.bind("<Next>", lambda e: self.outer_canvas.yview_scroll(1, "pages"), add="+")

        # 3. Klik & geser (Drag-to-scroll) pada area non-grafik untuk pengguna touchpad Windows
        if not isinstance(widget, HistogramView):
            widget.bind("<ButtonPress-1>", self._mulai_drag, add="+")
            widget.bind("<B1-Motion>", self._saat_drag, add="+")

        for child in widget.winfo_children():
            self._pasang_navigasi_scroll(child)

    def _mulai_drag(self, event):
        self.focus_set()
        self.outer_canvas.scan_mark(event.x, event.y)

    def _saat_drag(self, event):
        self.outer_canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mousewheel(self, event):
        if not self.winfo_exists():
            return
        self._wheel_acc += event.delta
        steps = int(self._wheel_acc / 30)
        if steps != 0:
            self._wheel_acc -= steps * 30
            self.outer_canvas.yview_scroll(-steps, "units")
        return "break"

    def _update_scrollregion(self, event=None):
        self.outer_canvas.configure(scrollregion=self.outer_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.outer_canvas.itemconfigure(self.win_id, width=event.width)
        self._update_scrollregion()

    def set_mode_dua_citra(self, tampil_kedua: bool):
        """Menampilkan kartu Histogram Citra Kedua saat operasi 2 gambar aktif."""
        if tampil_kedua:
            self.cards["hasil"].pack_forget()
            self.cards["kedua"].pack(fill=X, padx=14, pady=(4, 6))
            self.cards["hasil"].pack(fill=X, padx=14, pady=(4, 14))
            self._pasang_navigasi_scroll(self.cards["kedua"])
        else:
            self.cards["kedua"].pack_forget()
        self.update_idletasks()
        self._update_scrollregion()

    def set_data(self, kunci, data):
        """kunci = 'asli', 'kedua', atau 'hasil'; data = 256 angka atau None."""
        st = None if data is None else statistik_histogram(data)
        self.grafik[kunci].tampilkan(data, None if st is None else st["rata"])
        self.info[kunci].config(text=self._teks(st))
        self.update_idletasks()
        self._update_scrollregion()

    @staticmethod
    def _teks(st):
        if st is None:
            return "Belum ada citra."
        baris = [
            f"Total piksel: {format_angka(st['total'])}     Min: {st['min']}     "
            f"Maks: {st['maks']}     Rentang: {st['maks'] - st['min']}",
            f"Rata-rata: {format_desimal(st['rata'])}     Median: {st['median']}     "
            f"Modus: {st['modus']} ({format_angka(st['jumlah_modus'])} piksel)     "
            f"Std. deviasi: {format_desimal(st['std'])}",
            f"Gelap (0-85): {format_desimal(st['gelap'])}%     "
            f"Sedang (86-170): {format_desimal(st['sedang'])}%     "
            f"Terang (171-255): {format_desimal(st['terang'])}%",
            f"Kesan: {kesimpulan(st)}",
        ]
        return "\n".join(baris)

    def tutup(self):
        self.saat_ditutup()
        self.destroy()