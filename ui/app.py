"""Jendela utama aplikasi. Hanya mengurus tampilan; pengolahan citra
dikerjakan oleh paket `processing`."""
import webbrowser
import numpy as np
from PIL import Image, ImageTk
from tkinter import (Frame, Label, Canvas, Menu, Menubutton, Entry, IntVar, StringVar,
                     filedialog, messagebox, X, BOTH, LEFT, RIGHT, BOTTOM, CENTER,
                     FLAT, SOLID, END)

from config import *
from menu_structure import MENU_STRUCTURE, SHORTCUT
from riwayat import Riwayat
from processing import OPERASI, jalankan
from processing.histogram import hitung_histogram
from ui.widgets import FlatSlider, FlatButton, rounded_rect
from ui.about_view import AboutView
from ui.histogram_window import HistogramWindow

AKSI_FILE = {"file_open", "edit_undo", "edit_redo", "file_save", "file_saveas", "file_exit",
             "about_info", "about_github", "about_youtube"}
TIPE_FILE = [("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff", "*.webp"))]
TEKS_BELUM = "OPERASI AKTIF: BELUM DIPILIH (PILIH DARI MENU)"


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengolahan Citra Digital (PCD)")
        self.root.geometry("1000x700")
        self.root.minsize(820, 580)
        self.root.configure(bg=C_WIN)

        self.operasi_aktif = None
        self.img_asli = self.img_kedua = self.img_hasil = None
        self.tk_asli = self.tk_kedua = self.tk_hasil = None
        self.path_simpan = None
        self.param_min, self.param_max = 0, 255
        self.ket_hasil = None
        self.riwayat = Riwayat(20)
        self.entri_edit = {}
        self.jendela_hist = None

        self.buat_title_label()
        self.buat_menu()
        self.buat_status_bar()
        self.buat_workspace_view()
        self.aboutView = AboutView(self.root)
        self.show_workspace()
        self.pasang_shortcut()
        self.perbarui_menu_edit()

    # ---------------- Bagian atas ----------------
    def buat_title_label(self):
        bar = Frame(self.root, bg=C_TITLE)
        bar.pack(fill=X)
        Label(bar, text=APP_TITLE, bg=C_TITLE, fg=C_TEXT,
              font=(FONT, 8, "bold"), anchor="w", padx=14, pady=10).pack(fill=X)

    def buat_menu(self):
        self.menuBar = Frame(self.root, bg=C_MENU)
        self.menuBar.pack(fill=X)
        for nama, isi in MENU_STRUCTURE.items():
            mb = Menubutton(self.menuBar, text=nama, bg=C_MENU, fg=C_TEXT,
                            activebackground=C_MENU_HOVER, activeforeground=C_TEXT,
                            relief=FLAT, bd=0, padx=12, pady=8, font=(FONT, 9), cursor="hand2")
            mb.pack(side=LEFT)
            menu = self.buat_menu_baru(mb)
            mb.config(menu=menu)
            self.isi_menu(menu, isi)
        Frame(self.root, bg=C_LINE, height=1).pack(fill=X)

    def buat_menu_baru(self, parent):
        return Menu(parent, tearoff=0, bg="white", fg="#334155", bd=1, relief=SOLID,
                    activebackground="#e0f2fe", activeforeground=C_ACCENT, font=(FONT, 9))

    def isi_menu(self, parent, struktur):
        for label, nilai in struktur.items():
            if nilai is None:
                parent.add_separator()
            elif isinstance(nilai, dict):
                sub = self.buat_menu_baru(parent)
                parent.add_cascade(label=label, menu=sub)
                self.isi_menu(sub, nilai)
            else:
                siap = nilai in AKSI_FILE or nilai in OPERASI
                parent.add_command(label=label, command=lambda k=nilai: self.menu_click(k),
                                   accelerator=SHORTCUT.get(nilai, ""),
                                   state="normal" if siap else "disabled")
                if nilai in ("edit_undo", "edit_redo"):
                    self.entri_edit[nilai] = (parent, parent.index("end"))

    def menu_click(self, kode):
        aksi = {
            "file_open": self.buka_citra_asli,
            "edit_undo": self.undo,
            "edit_redo": self.redo,
            "file_save": self.simpan_citra,
            "file_saveas": self.simpan_citra_sebagai,
            "file_exit": self.root.destroy,
            "about_info": self.show_about,
            "about_github": lambda: webbrowser.open(GITHUB_URL),
            "about_youtube": lambda: webbrowser.open(YOUTUBE_URL),
        }
        if kode in aksi:
            aksi[kode]()
            return

        info = OPERASI[kode]
        self.catat_riwayat()
        self.show_workspace()
        self.operasi_aktif = kode
        self.atur_mode_dua_citra(info["dua_citra"])
        self.atur_parameter(info)
        self.atur_tombol_histogram(info.get("histogram", False))
        self.update_indikator_operasi(f"OPERASI AKTIF: {kode.upper()}", aktif=True)
        if info["dua_citra"]:
            self.set_status(f"Operasi dipilih: {kode} (Memerlukan 2 citra / nilai parameter)")
        else:
            self.set_status(f"Operasi dipilih: {kode}")
        if self.img_asli is not None:
            self._proses()

    def update_indikator_operasi(self, teks, aktif=False):
        if aktif:
            self.lbl_op_tengah.config(text=f"  ⚡ {teks}  ", bg="#e0f2fe", fg=C_ACCENT,
                                      highlightbackground="#7dd3fc")
        else:
            self.lbl_op_tengah.config(text=f"  {teks}  ", bg="#f1f5f9", fg=C_TITLE_CARD,
                                      highlightbackground="#cbd5e1")

    def atur_tombol_histogram(self, tampil: bool):
        """Menampilkan tombol Histogram hanya pada operasi yang membutuhkan analisis histogram."""
        if tampil:
            self.btn_hist.place(relx=1.0, rely=0.5, anchor="e")
            self._sinkron_mode_histogram()
        else:
            self.btn_hist.place_forget()
            if self.jendela_hist is not None:
                self.jendela_hist.tutup()

    # ---------------- Parameter ----------------
    def atur_parameter(self, info):
        """Menyesuaikan slider dengan rentang milik operasi yang dipilih."""
        if info["param"] is None:
            self.lbl_param.config(text="Parameter: (tidak diperlukan)")
            self.ent_param.grid_remove()
            self.slider.grid_remove()
            return
        pmin, pmaks, awal = info["param"]
        self.param_min, self.param_max = pmin, pmaks
        self.slider.set_range(pmin, pmaks)
        self.param_var.set(awal)
        self.lbl_param.config(text=f"{info['label']} [{pmin}..{pmaks}]:")
        self.ent_param.grid()
        self.slider.grid()

    def commit_param(self, event=None):
        raw = self.param_str.get().strip()
        try:
            nilai_awal = int(float(raw))
        except ValueError:
            nilai_awal = self.param_var.get()
            self.set_status("Input tidak valid, dikembalikan ke nilai sebelumnya")

        nilai = max(self.param_min, min(self.param_max, nilai_awal))
        self.param_var.set(nilai)
        self.param_str.set(str(nilai))

        # Umpan balik non-blocking di Status Bar + kilatan merah singkat jika melebihi batas
        if nilai != nilai_awal:
            self.set_status(
                f"Nilai {nilai_awal} melebihi batas [{self.param_min}..{self.param_max}], disesuaikan ke {nilai}"
            )
            self.ent_param.config(highlightbackground="#ef4444", highlightcolor="#ef4444")
            self.root.after(
                900,
                lambda: self.ent_param.config(highlightbackground="#dcdcdc", highlightcolor=C_ACCENT)
            )

        if event is not None and event.keysym in ("Return", "KP_Enter"):
            self.workspaceView.focus_set()
            if self.img_asli is not None and self.operasi_aktif:
                self.terapkan_operasi()

    # ---------------- Tata letak utama ----------------
    def buat_workspace_view(self):
        self.workspaceView = Frame(self.root, bg=C_WIN)

        top = Frame(self.workspaceView, bg=C_WIN)
        top.pack(fill=X, padx=26, pady=(14, 0))
        self.lbl_op_tengah = Label(top, text=f"  {TEKS_BELUM}  ", bg="#f1f5f9", fg=C_TITLE_CARD,
                                   font=(FONT, 9, "bold"), padx=16, pady=6,
                                   highlightthickness=1, highlightbackground="#cbd5e1")
        self.lbl_op_tengah.pack(anchor=CENTER)
        self.btn_hist = FlatButton(top, "Histogram", self.buka_histogram)
        # Disembunyikan saat awal hingga operasi yang memerlukan histogram dipilih

        wrapper = Frame(self.workspaceView, bg=C_WIN)
        wrapper.pack(fill=BOTH, expand=True, padx=26, pady=(12, 14))
        self.wrapper = wrapper
        wrapper.columnconfigure(0, weight=1, uniform="k")
        wrapper.columnconfigure(2, weight=1, uniform="k")
        wrapper.rowconfigure(0, weight=1)

        self.card_asli, self.cv_asli, self.ph_asli = self.buat_kartu(
            wrapper, 0, "CITRA ASLI (ORIGINAL)", "[ Placeholder Gambar Asli ]", self.buka_citra_asli)
        self.card_kedua, self.cv_kedua, self.ph_kedua = self.buat_kartu(
            wrapper, 1, "CITRA KEDUA (SECOND)", "[ Placeholder Gambar Kedua ]", self.buka_citra_kedua)
        self.card_hasil, self.cv_hasil, self.ph_hasil = self.buat_kartu(
            wrapper, 2, "CITRA HASIL (PROCESSED)", "[ Placeholder Gambar Hasil ]")

        self.atur_mode_dua_citra(False)
        self.buat_panel_kontrol()

    def buat_kartu(self, parent, kolom, judul, teks_placeholder, open_cmd=None):
        card = Frame(parent, bg=C_CARD, padx=12, pady=12,
                     highlightthickness=1, highlightbackground="#e2e8f0")
        card.grid(row=0, column=kolom, sticky="nsew", padx=6)
        Label(card, text=judul, bg=C_CARD, fg=C_TITLE_CARD,
              font=(FONT, 9, "bold")).pack(pady=(0, 8))

        canvas = Canvas(card, bg=C_CANVAS, highlightthickness=0)
        canvas.pack(fill=BOTH, expand=True)
        ph = canvas.create_text(0, 0, text=teks_placeholder, fill=C_MUTED, font=(FONT, 8))

        canvas.btn_id = None
        canvas.img_id = None
        if open_cmd is not None:
            btn = FlatButton(canvas, "Open...", open_cmd)
            canvas.btn_id = canvas.create_window(0, 0, window=btn)

        def reposisi(e):
            w, h = max(e.width, 2), max(e.height, 2)
            ada_tombol = canvas.btn_id is not None
            canvas.coords(ph, w // 2, h // 2 - (18 if ada_tombol else 0))
            if ada_tombol:
                canvas.coords(canvas.btn_id, w // 2, h // 2 + 14)
            self.refresh_canvas_image(canvas)

        canvas.bind("<Configure>", reposisi)
        return card, canvas, ph

    def buat_panel_kontrol(self):
        holder = Canvas(self.workspaceView, height=92, bg=C_WIN, highlightthickness=0)
        holder.pack(fill=X, padx=26, pady=(0, 20))

        inner = Frame(holder, bg="white")
        Label(inner, text="PANEL KONTROL PARAMETER OPERASI", bg="white", fg=C_TITLE_CARD,
              font=(FONT, 7, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        self.lbl_param = Label(inner, text="Parameter:", bg="white", fg=C_TEXT,
                               font=(FONT, 8, "bold"))
        self.lbl_param.grid(row=1, column=0, sticky="w")

        self.param_var = IntVar(value=50)
        self.param_str = StringVar(value=str(self.param_var.get()))
        self.param_var.trace_add("write", lambda *a: self.param_str.set(str(self.param_var.get())))
        self.ent_param = Entry(inner, textvariable=self.param_str, width=5, justify=CENTER,
                               bg="white", fg=C_ACCENT, relief=FLAT, font=(FONT, 8, "bold"),
                               insertbackground=C_ACCENT, highlightthickness=1,
                               highlightbackground="#dcdcdc", highlightcolor=C_ACCENT,
                               cursor="xterm")
        self.ent_param.grid(row=1, column=1, sticky="w", padx=(4, 4))
        self.ent_param.bind("<Return>", self.commit_param)
        self.ent_param.bind("<KP_Enter>", self.commit_param)
        self.ent_param.bind("<FocusOut>", self.commit_param)
        self.ent_param.bind(
            "<FocusIn>", lambda e: self.ent_param.after_idle(lambda: self.ent_param.select_range(0, END)))

        self.slider = FlatSlider(inner, 0, 255, self.param_var)
        self.slider.grid(row=1, column=2, sticky="ew", padx=8)

        btns = Frame(inner, bg="white")
        btns.grid(row=1, column=3, sticky="e")
        FlatButton(btns, "Terapkan Operasi", self.terapkan_operasi).pack(side=LEFT, padx=(0, 8))
        FlatButton(btns, "Reset Operasi", self.reset_operasi).pack(side=LEFT, padx=(0, 8))
        FlatButton(btns, "Hapus Citra", self.hapus_citra, bg="#ef4444", hover="#dc2626",
                   fg="white").pack(side=LEFT)
        inner.columnconfigure(2, weight=1)

        win = holder.create_window(20, 12, window=inner, anchor="nw")

        def gambar(e):
            holder.delete("bg")
            rounded_rect(holder, 1, 1, e.width - 2, e.height - 2, 10,
                         fill="white", outline="#dcdcdc", tags="bg")
            holder.tag_lower("bg")
            holder.itemconfigure(win, width=e.width - 40)
        holder.bind("<Configure>", gambar)

    def buat_status_bar(self):
        self.statusBar = Frame(self.root, bg=C_TITLE)
        self.statusBar.pack(side=BOTTOM, fill=X)
        Frame(self.statusBar, bg=C_LINE, height=1).pack(fill=X)
        row = Frame(self.statusBar, bg=C_TITLE)
        row.pack(fill=X)
        self.lbl_status = Label(row, text="Status: Siap", bg=C_TITLE, fg=C_MUTED,
                                font=(FONT, 8), padx=14, pady=10)
        self.lbl_status.pack(side=LEFT)
        self.lbl_info = Label(row, text="Resolusi: - | Zoom: 100%", bg=C_TITLE,
                              fg=C_MUTED, font=(FONT, 8), padx=14)
        self.lbl_info.pack(side=RIGHT)

    # ---------------- Tampilan citra & Histogram ----------------
    def _data_histogram(self, pil_img):
        return None if pil_img is None else hitung_histogram(np.array(pil_img, dtype=np.uint8))

    def _perlu_hist_kedua(self):
        if not self.operasi_aktif:
            return False
        info = OPERASI.get(self.operasi_aktif, {})
        return bool(info.get("dua_citra") and info.get("histogram"))

    def _sinkron_mode_histogram(self):
        if self.jendela_hist is None:
            return
        tampil_kedua = self._perlu_hist_kedua()
        self.jendela_hist.set_mode_dua_citra(tampil_kedua)
        if tampil_kedua:
            self.jendela_hist.set_data("kedua", self._data_histogram(self.img_kedua))

    def perbarui_histogram(self, canvas, pil_img):
        """Memperbarui jendela histogram bila sedang terbuka."""
        if self.jendela_hist is None:
            return
        if canvas is self.cv_asli:
            self.jendela_hist.set_data("asli", self._data_histogram(pil_img))
        elif canvas is self.cv_kedua:
            self._sinkron_mode_histogram()
        elif canvas is self.cv_hasil:
            self.jendela_hist.set_data("hasil", self._data_histogram(pil_img))

    def buka_histogram(self):
        if self.jendela_hist is not None:
            self.jendela_hist.lift()
            self.jendela_hist.focus_force()
            return
        self.jendela_hist = HistogramWindow(self.root, self._histogram_ditutup)
        self._sinkron_mode_histogram()
        self.jendela_hist.set_data("asli", self._data_histogram(self.img_asli))
        self.jendela_hist.set_data("hasil", self._data_histogram(self.img_hasil))

    def _histogram_ditutup(self):
        self.jendela_hist = None

    def tampilkan_pada_canvas(self, canvas, ph_id, pil_img, attr_tk_name):
        self.perbarui_histogram(canvas, pil_img)
        if pil_img is None:
            if canvas.img_id is not None:
                canvas.delete(canvas.img_id)
                canvas.img_id = None
            canvas.itemconfigure(ph_id, state="normal")
            if canvas.btn_id is not None:
                canvas.itemconfigure(canvas.btn_id, state="normal")
            setattr(self, attr_tk_name, None)
            return

        w = max(canvas.winfo_width(), 10)
        h = max(canvas.winfo_height(), 10)
        img_copy = pil_img.copy()
        img_copy.thumbnail((max(w - 8, 10), max(h - 8, 10)), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img_copy)
        setattr(self, attr_tk_name, tk_img)

        canvas.itemconfigure(ph_id, state="hidden")
        if canvas.btn_id is not None:
            canvas.itemconfigure(canvas.btn_id, state="hidden")
        if canvas.img_id is None:
            canvas.img_id = canvas.create_image(w // 2, h // 2, image=tk_img, anchor=CENTER)
        else:
            canvas.coords(canvas.img_id, w // 2, h // 2)
            canvas.itemconfigure(canvas.img_id, image=tk_img)

    def refresh_canvas_image(self, canvas):
        if canvas == self.cv_asli and self.img_asli is not None:
            self.tampilkan_pada_canvas(self.cv_asli, self.ph_asli, self.img_asli, "tk_asli")
        elif canvas == self.cv_kedua and self.img_kedua is not None:
            self.tampilkan_pada_canvas(self.cv_kedua, self.ph_kedua, self.img_kedua, "tk_kedua")
        elif canvas == self.cv_hasil and self.img_hasil is not None:
            self.tampilkan_pada_canvas(self.cv_hasil, self.ph_hasil, self.img_hasil, "tk_hasil")

    def atur_mode_dua_citra(self, dua_citra):
        if dua_citra:
            self.card_kedua.grid(row=0, column=1, sticky="nsew", padx=6)
            self.wrapper.columnconfigure(1, weight=1, uniform="k")
        else:
            self.card_kedua.grid_remove()
            self.wrapper.columnconfigure(1, weight=0, minsize=0, uniform="")

    # ---------------- Manajemen file ----------------
    def buka_citra_asli(self):
        path = filedialog.askopenfilename(title="Pilih Citra Asli", filetypes=TIPE_FILE)
        if not path:
            return
        try:
            baru = Image.open(path).convert("RGB")
            self.catat_riwayat()
            self.img_asli = baru
            self.tampilkan_pada_canvas(self.cv_asli, self.ph_asli, self.img_asli, "tk_asli")
            w, h = self.img_asli.size
            self.lbl_info.config(text=f"Resolusi: {w}x{h} px | Zoom: Fit")
            self.set_status(f"Citra asli berhasil dimuat ({w}x{h} px)")
            if self.operasi_aktif and self.img_asli is not None:
                self._proses()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka citra:\n{e}")

    def buka_citra_kedua(self):
        path = filedialog.askopenfilename(title="Pilih Citra Kedua", filetypes=TIPE_FILE)
        if not path:
            return
        try:
            baru = Image.open(path).convert("RGB")
            self.catat_riwayat()
            self.img_kedua = baru
            self.tampilkan_pada_canvas(self.cv_kedua, self.ph_kedua, self.img_kedua, "tk_kedua")
            w, h = self.img_kedua.size
            self.set_status(f"Citra kedua berhasil dimuat ({w}x{h} px)")
            if self.operasi_aktif and self.img_asli is not None:
                self._proses()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka citra kedua:\n{e}")

    def simpan_citra(self):
        if self.img_hasil is None:
            messagebox.showwarning("Peringatan", "Belum ada citra hasil untuk disimpan!")
            return
        if self.path_simpan:
            self.img_hasil.save(self.path_simpan)
            self.set_status(f"Citra hasil disimpan ke: {self.path_simpan}")
        else:
            self.simpan_citra_sebagai()

    def simpan_citra_sebagai(self):
        if self.img_hasil is None:
            messagebox.showwarning("Peringatan", "Belum ada citra hasil untuk disimpan!")
            return
        path = filedialog.asksaveasfilename(
            title="Simpan Citra Hasil", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if path:
            self.path_simpan = path
            self.img_hasil.save(path)
            self.set_status(f"Citra hasil disimpan sebagai: {path}")

    # ---------------- Navigasi ----------------
    def show_workspace(self):
        self.aboutView.pack_forget()
        self.workspaceView.pack(fill=BOTH, expand=True)

    def show_about(self):
        self.workspaceView.pack_forget()
        self.aboutView.pack(fill=BOTH, expand=True)
        self.set_status("Menampilkan info tim developer")

    def set_status(self, teks):
        self.lbl_status.config(text=f"Status: {teks}")

    # ---------------- Menjalankan operasi ----------------
    def terapkan_operasi(self):
        if self.img_asli is None:
            messagebox.showinfo("Info", "Silakan buka Citra Asli terlebih dahulu (File > Open atau tombol Open).")
            return
        if not self.operasi_aktif:
            messagebox.showinfo("Info", "Silakan pilih operasi pada menu terlebih dahulu.")
            return

        self.catat_riwayat()
        self._proses()

    def _proses(self):
        """Menjalankan operasi aktif (tanpa mencatat riwayat)."""
        img = np.array(self.img_asli, dtype=np.uint8)
        img2 = np.array(self.img_kedua, dtype=np.uint8) if self.img_kedua is not None else None
        hasil, ket = jalankan(self.operasi_aktif, img, self.param_var.get(), img2)

        self.img_hasil = Image.fromarray(hasil)
        self.ket_hasil = ket
        self.tampilkan_pada_canvas(self.cv_hasil, self.ph_hasil, self.img_hasil, "tk_hasil")
        self.update_indikator_operasi(f"OPERASI AKTIF: {ket.upper()}", aktif=True)
        self.set_status(f"Berhasil menerapkan {ket}")

    def reset_operasi(self):
        self.catat_riwayat()
        self._kosongkan_operasi()

    def _kosongkan_operasi(self):
        self.operasi_aktif = None
        self.img_hasil = None
        self.ket_hasil = None
        self.tampilkan_pada_canvas(self.cv_hasil, self.ph_hasil, None, "tk_hasil")
        self.param_var.set(50)
        self.lbl_param.config(text="Parameter:")
        self.ent_param.grid()
        self.slider.grid()
        self.update_indikator_operasi(TEKS_BELUM, aktif=False)
        self.atur_mode_dua_citra(False)
        self.atur_tombol_histogram(False)
        self.set_status("Reset operasi berhasil")

    def hapus_citra(self):
        self.catat_riwayat()
        self._kosongkan_operasi()
        self.img_asli = self.img_kedua = None
        self.path_simpan = None
        self.tampilkan_pada_canvas(self.cv_asli, self.ph_asli, None, "tk_asli")
        self.tampilkan_pada_canvas(self.cv_kedua, self.ph_kedua, None, "tk_kedua")
        self.lbl_info.config(text="Resolusi: - | Zoom: 100%")
        self.set_status("Seluruh citra dibersihkan")

    # ---------------- Undo / Redo ----------------
    def _ambil_state(self):
        return {"asli": self.img_asli, "kedua": self.img_kedua, "hasil": self.img_hasil,
                "operasi": self.operasi_aktif, "param": self.param_var.get(),
                "ket": self.ket_hasil, "path": self.path_simpan}

    def catat_riwayat(self):
        self.riwayat.catat(self._ambil_state())
        self.perbarui_menu_edit()

    def undo(self):
        state = self.riwayat.undo(self._ambil_state())
        if state is None:
            self.set_status("Tidak ada langkah yang bisa di-undo")
            return
        self._pulihkan(state)
        self.set_status("Undo berhasil")

    def redo(self):
        state = self.riwayat.redo(self._ambil_state())
        if state is None:
            self.set_status("Tidak ada langkah yang bisa di-redo")
            return
        self._pulihkan(state)
        self.set_status("Redo berhasil")

    def _pulihkan(self, s):
        self.img_asli, self.img_kedua, self.img_hasil = s["asli"], s["kedua"], s["hasil"]
        self.operasi_aktif, self.ket_hasil, self.path_simpan = s["operasi"], s["ket"], s["path"]

        self.tampilkan_pada_canvas(self.cv_asli, self.ph_asli, self.img_asli, "tk_asli")
        self.tampilkan_pada_canvas(self.cv_kedua, self.ph_kedua, self.img_kedua, "tk_kedua")
        self.tampilkan_pada_canvas(self.cv_hasil, self.ph_hasil, self.img_hasil, "tk_hasil")

        if self.operasi_aktif:
            info = OPERASI[self.operasi_aktif]
            self.atur_mode_dua_citra(info["dua_citra"])
            self.atur_parameter(info)
            self.atur_tombol_histogram(info.get("histogram", False))
            self.param_var.set(s["param"])
            teks = self.ket_hasil if (self.img_hasil is not None and self.ket_hasil) else self.operasi_aktif
            self.update_indikator_operasi(f"OPERASI AKTIF: {teks.upper()}", aktif=True)
        else:
            self.atur_mode_dua_citra(False)
            self.atur_tombol_histogram(False)
            self.param_var.set(50)
            self.lbl_param.config(text="Parameter:")
            self.ent_param.grid()
            self.slider.grid()
            self.update_indikator_operasi(TEKS_BELUM, aktif=False)

        if self.img_asli is not None:
            w, h = self.img_asli.size
            self.lbl_info.config(text=f"Resolusi: {w}x{h} px | Zoom: Fit")
        else:
            self.lbl_info.config(text="Resolusi: - | Zoom: 100%")
        self.perbarui_menu_edit()

    def perbarui_menu_edit(self):
        """Item Undo/Redo di menu nonaktif bila riwayat kosong."""
        status = {"edit_undo": self.riwayat.bisa_undo, "edit_redo": self.riwayat.bisa_redo}
        for kode, (menu, indeks) in self.entri_edit.items():
            menu.entryconfig(indeks, state="normal" if status[kode] else "disabled")

    # ---------------- Shortcut keyboard ----------------
    def pasang_shortcut(self):
        self.root.bind_all("<Control-KeyPress>", self.on_ctrl)

    def on_ctrl(self, event):
        if isinstance(self.root.focus_get(), Entry):
            return
        tombol = event.keysym.lower()
        shift = bool(event.state & 0x1)   # dibaca dari state agar aman saat Caps Lock aktif
        peta = {
            ("z", False): self.undo,
            ("y", False): self.redo,
            ("o", False): self.buka_citra_asli,
            ("s", False): self.simpan_citra,
            ("s", True): self.simpan_citra_sebagai,
            ("q", False): self.root.destroy,
        }
        aksi = peta.get((tombol, shift))
        if aksi:
            aksi()
            return "break"
