"""Enhancement: Brightness, Contrast, Hist. Equalization, Smoothing,
Sharpening (spatial & frequency domain), Geometrics correction."""
import numpy as np
import cv2
from . import daftar


def _ganjil(p, minimum=1):
    """Ukuran kernel harus ganjil."""
    return max(minimum, 2 * (int(p) // 2) + 1)


def _filter_frekuensi(img, buat_mask):
    """Menerapkan mask pada domain frekuensi untuk tiap kanal warna."""
    H, W = img.shape[:2]
    v, u = np.ogrid[:H, :W]
    D = np.sqrt((u - W / 2.0) ** 2 + (v - H / 2.0) ** 2)
    mask = buat_mask(D).astype(np.float32)
    hasil = np.zeros(img.shape, dtype=np.float32)
    for c in range(3):
        F = np.fft.fftshift(np.fft.fft2(img[:, :, c].astype(np.float32)))
        hasil[:, :, c] = np.real(np.fft.ifft2(np.fft.ifftshift(F * mask)))
    return hasil


# ---------------- Brightness / Contrast / Histogram ----------------
@daftar("Brightness", param=(-100, 100, 40), label="Tingkat kecerahan", histogram=True)
def brightness(img, p, img2=None):
    return cv2.convertScaleAbs(img, alpha=1.0, beta=p), f"Brightness ({p:+d})"


@daftar("Contrast", param=(10, 300, 150), label="Kontras (%)", histogram=True)
def contrast(img, p, img2=None):
    alpha = p / 100.0
    hasil = np.clip(alpha * (img.astype(np.float32) - 128.0) + 128.0, 0, 255).astype(np.uint8)
    return hasil, f"Contrast ({alpha:.2f}x)"


@daftar("Hist. Equalization", histogram=True)
def hist_eq(img, p, img2=None):
    ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB), "Hist. Equalization"


# ---------------- Smoothing: spatial ----------------
@daftar("Lowpass Filtering", param=(1, 25, 5), label="Ukuran kernel", histogram=False)
def lowpass(img, p, img2=None):
    k = _ganjil(p)
    return cv2.blur(img, (k, k)), f"Lowpass / Mean ({k}x{k})  |  Library: cv2.blur()"


@daftar("Median Filtering", param=(1, 15, 3), label="Ukuran kernel", histogram=False)
def median(img, p, img2=None):
    k = _ganjil(p, 3)
    return cv2.medianBlur(img, k), f"Median ({k}x{k})"


# ---------------- Smoothing: frequency ----------------
@daftar("ILPF", param=(1, 200, 40), label="Frekuensi cutoff D0", histogram=False)
def ilpf(img, p, img2=None):
    out = _filter_frekuensi(img, lambda D: D <= p)
    return np.clip(out, 0, 255).astype(np.uint8), f"ILPF (D0={p})"


@daftar("BLPF", param=(1, 200, 40), label="Frekuensi cutoff D0 (orde 2)", histogram=False)
def blpf(img, p, img2=None):
    out = _filter_frekuensi(img, lambda D: 1.0 / (1.0 + (D / p) ** 4))
    return np.clip(out, 0, 255).astype(np.uint8), f"BLPF (D0={p}, n=2)"


# ---------------- Sharpening: spatial ----------------
@daftar("Highpass Filtering", param=(1, 25, 5), label="Ukuran kernel blur", histogram=False)
def highpass(img, p, img2=None):
    k = _ganjil(p)
    hp = img.astype(np.float32) - cv2.blur(img, (k, k)).astype(np.float32)
    return np.clip(hp + 128.0, 0, 255).astype(np.uint8), f"Highpass ({k}x{k}, offset 128)"


@daftar("Highboost Filtering", param=(10, 50, 15), label="Faktor boost (x10)", histogram=False)
def highboost(img, p, img2=None):
    A = p / 10.0
    f = img.astype(np.float32)
    mask = f - cv2.GaussianBlur(img, (5, 5), 0).astype(np.float32)
    return np.clip(f + A * mask, 0, 255).astype(np.uint8), f"Highboost (A={A:.1f})"


# ---------------- Sharpening: frequency ----------------
@daftar("IHPF", param=(1, 200, 30), label="Frekuensi cutoff D0", histogram=False)
def ihpf(img, p, img2=None):
    out = _filter_frekuensi(img, lambda D: D > p)
    return np.clip(out + 128.0, 0, 255).astype(np.uint8), f"IHPF (D0={p}, offset 128)"


@daftar("BHPF", param=(1, 200, 30), label="Frekuensi cutoff D0 (orde 2)", histogram=False)
def bhpf(img, p, img2=None):
    out = _filter_frekuensi(img, lambda D: 1.0 / (1.0 + (p / np.maximum(D, 1e-6)) ** 4))
    return np.clip(out + 128.0, 0, 255).astype(np.uint8), f"BHPF (D0={p}, n=2, offset 128)"


# ---------------- Geometrics correction ----------------
@daftar("Geometrics correction", param=(-50, 50, 20), label="Koreksi distorsi lensa (+ barrel, - pincushion)", histogram=False)
def geo_correction(img, p, img2=None):
    H, W = img.shape[:2]
    k = p / 100.0
    xs, ys = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    nx, ny = (xs - W / 2.0) / (W / 2.0), (ys - H / 2.0) / (H / 2.0)
    faktor = 1.0 + k * (nx ** 2 + ny ** 2)
    map_x = (nx * faktor * (W / 2.0) + W / 2.0).astype(np.float32)
    map_y = (ny * faktor * (H / 2.0) + H / 2.0).astype(np.float32)
    hasil = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
    return hasil, f"Geometrics correction (k={k:+.2f})"
