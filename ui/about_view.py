"""Halaman 'Tentang Tim Pengembang'."""
import webbrowser
from tkinter import Frame, Label, CENTER, X, LEFT
from config import ANGGOTA, GITHUB_URL, YOUTUBE_URL, C_WIN, C_TEXT, FONT
from ui.widgets import FlatButton


class AboutView(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_WIN)
        card = Frame(self, bg="white", highlightthickness=1,
                     highlightbackground="#dcdcdc", padx=40, pady=32)
        card.place(relx=0.5, rely=0.42, anchor=CENTER)

        Label(card, text="Tentang Tim Pengembang", bg="white", fg=C_TEXT,
              font=(FONT, 15, "bold")).pack()
        Label(card, text="Pengolahan Citra Digital (PCD)", bg="white", fg="#64748b",
              font=(FONT, 10)).pack(pady=(2, 16))

        box = Frame(card, bg="#f8fafc", highlightthickness=1,
                    highlightbackground="#e2e8f0", padx=18, pady=12)
        box.pack(fill=X, pady=(0, 18))
        Label(box, text="Anggota Kelompok:", bg="#f8fafc", fg="#334155",
              font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 6))
        for i, nama in enumerate(ANGGOTA, 1):
            Label(box, text=f"{i}. {nama}", bg="#f8fafc", fg="#475569",
                  font=(FONT, 10)).pack(anchor="w")

        row = Frame(card, bg="white")
        row.pack()
        FlatButton(row, "💻 Link Repository GitHub", lambda: webbrowser.open(GITHUB_URL),
                   bg="#1e293b", hover="#0f172a", fg="white").pack(side=LEFT, padx=6)
        FlatButton(row, "▶ Link Video YouTube", lambda: webbrowser.open(YOUTUBE_URL),
                   bg="#ef4444", hover="#dc2626", fg="white").pack(side=LEFT, padx=6)
