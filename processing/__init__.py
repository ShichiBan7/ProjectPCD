import numpy as np
import cv2

OPERASI = {}


def daftar(nama, dua_citra=False, param=None, label="Parameter", histogram=False,
           param2=None, label2="Parameter 2"):
    """Mendaftarkan sebuah fungsi sebagai operasi.

    param = None                  -> operasi tanpa parameter (slider disembunyikan)
    param = (minimum, maks, awal) -> rentang dan nilai awal slider
    histogram = True              -> tombol Histogram ditampilkan untuk operasi ini
    param2 = (minimum, maks, awal) -> slider kedua (independen); nilainya dikirim sebagai
                                      argumen p2 ke fungsi operasi
    """
    def pembungkus(fungsi):
        OPERASI[nama] = {
            "fungsi": fungsi,
            "dua_citra": dua_citra,
            "param": param,
            "label": label,
            "histogram": histogram,
            "param2": param2,
            "label2": label2,
        }
        return fungsi
    return pembungkus


def citra_kedua(img, img2, p):
    """Citra kedua disesuaikan ukurannya; jika kosong, dipakai matriks bernilai |p|."""
    h, w, c = img.shape
    if img2 is not None:
        return cv2.resize(img2, (w, h), interpolation=cv2.INTER_LINEAR)
    val_u8 = int(np.clip(abs(p), 0, 255))
    return np.full((h, w, c), val_u8, dtype=np.uint8)


def jalankan(nama, img, p, img2=None):
    return OPERASI[nama]["fungsi"](img, p, img2)


# Impor modul di bawah ini agar semua operasi otomatis terdaftar.
from . import basic_ops, colouring, enhancement, noise, edge_detection  # noqa: E402,F401
