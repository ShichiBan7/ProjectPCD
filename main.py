"""Titik masuk aplikasi. Jalankan dengan:  python main.py"""
import tkinter as tk
from ui.app import ImageProcessingApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
