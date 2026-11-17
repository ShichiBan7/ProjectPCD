"""Perhitungan histogram dan statistiknya (tanpa Tkinter)."""
import numpy as np
import cv2

BATAS_GELAP = 85      # 0-85   = zona gelap
BATAS_TERANG = 170    # 171-255 = zona terang


def hitung_histogram(img_rgb):
    """Mengembalikan 256 angka: jumlah piksel untuk tiap tingkat kecerahan 0-255."""
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    return cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()


def statistik_histogram(hist):
    """Ringkasan angka dari histogram. Mengembalikan None jika histogram kosong."""
    hist = np.asarray(hist, dtype=np.float64)
    total = float(hist.sum())
    if total <= 0:
        return None
    nilai = np.arange(256)
    rata = float((hist * nilai).sum() / total)
    std = float(np.sqrt((hist * (nilai - rata) ** 2).sum() / total))
    ada = np.nonzero(hist)[0]
    modus = int(np.argmax(hist))
    return {
        "total": int(total),
        "min": int(ada.min()),
        "maks": int(ada.max()),
        "rata": rata,
        "median": int(np.searchsorted(np.cumsum(hist), total / 2.0)),
        "modus": modus,
        "jumlah_modus": int(hist[modus]),
        "std": std,
        "gelap": float(hist[:BATAS_GELAP + 1].sum() / total * 100),
        "sedang": float(hist[BATAS_GELAP + 1:BATAS_TERANG + 1].sum() / total * 100),
        "terang": float(hist[BATAS_TERANG + 1:].sum() / total * 100),
    }


def kesimpulan(st):
    """Kalimat pendek untuk membantu membaca grafik (ambang bersifat pedoman)."""
    kecerahan = "gelap" if st["rata"] <= BATAS_GELAP else ("terang" if st["rata"] > BATAS_TERANG else "sedang")
    kontras = "rendah" if st["std"] < 40 else ("tinggi" if st["std"] >= 70 else "sedang")
    return f"Citra cenderung {kecerahan}, kontras {kontras}"
