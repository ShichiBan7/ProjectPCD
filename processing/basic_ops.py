import numpy as np
import cv2
from . import daftar, citra_kedua

LABEL_NILAI = "Nilai skalar (dipakai jika citra kedua kosong)"


# ---------------- Negative ----------------
@daftar("Negative", histogram=True)
def negative(img, p, img2=None):
    return cv2.bitwise_not(img), "Negative"


# ---------------- Arithmetic ----------------
@daftar("Add", dua_citra=True, param=(-255, 255, 50), label=LABEL_NILAI, histogram=True)
def add(img, p, img2=None):
    if img2 is not None:
        hasil = cv2.add(img, citra_kedua(img, img2, p))
    else:
        hasil = cv2.convertScaleAbs(img, alpha=1.0, beta=float(p))
    return hasil, "Arithmetic Add (+)"


@daftar("Substract", dua_citra=True, param=(-255, 255, 50), label=LABEL_NILAI, histogram=True)
def substract(img, p, img2=None):
    if img2 is not None:
        hasil = cv2.subtract(img, citra_kedua(img, img2, p))
    else:
        hasil = cv2.convertScaleAbs(img, alpha=1.0, beta=float(-p))
    return hasil, "Arithmetic Substract (-)"


@daftar("Multiply", dua_citra=True, param=(0, 255, 128), label=LABEL_NILAI, histogram=True)
def multiply(img, p, img2=None):
    if img2 is not None:
        hasil = cv2.multiply(img, citra_kedua(img, img2, p), scale=1.0 / 255.0)
    else:
        hasil = cv2.convertScaleAbs(img, alpha=max(p / 128.0, 0.0), beta=0)
    return hasil, "Arithmetic Multiply (*)"


@daftar("Divide", dua_citra=True, param=(1, 255, 64), label=LABEL_NILAI, histogram=True)
def divide(img, p, img2=None):
    if img2 is not None:
        pembagi = np.maximum(citra_kedua(img, img2, p), 1)
        hasil = cv2.divide(img, pembagi, scale=255.0)
    else:
        hasil = cv2.convertScaleAbs(img, alpha=1.0 / max(p / 64.0, 0.1), beta=0)
    return hasil, "Arithmetic Divide (/)"


# ---------------- Boolean ----------------
@daftar("NOT", histogram=False)
def op_not(img, p, img2=None):
    return cv2.bitwise_not(img), "Boolean NOT"


@daftar("AND", dua_citra=True, param=(0, 255, 128), label=LABEL_NILAI, histogram=False)
def op_and(img, p, img2=None):
    return cv2.bitwise_and(img, citra_kedua(img, img2, p)), "Boolean AND"


@daftar("OR", dua_citra=True, param=(0, 255, 128), label=LABEL_NILAI, histogram=False)
def op_or(img, p, img2=None):
    return cv2.bitwise_or(img, citra_kedua(img, img2, p)), "Boolean OR"


@daftar("XOR", dua_citra=True, param=(0, 255, 128), label=LABEL_NILAI, histogram=False)
def op_xor(img, p, img2=None):
    return cv2.bitwise_xor(img, citra_kedua(img, img2, p)), "Boolean XOR"

# ---------------- Geometrics ----------------
@daftar("Translation", param=(-200, 200, 50), label="Pergeseran sumbu X (tx)", histogram=False,
        param2=(-200, 200, 25), label2="Pergeseran sumbu Y (ty)")
def translation(img, p, img2=None, p2=0):
    H, W, _ = img.shape
    tx, ty = float(p), float(p2)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    hasil = cv2.warpAffine(img, M, (W, H))
    return hasil, f"Geometrics: Translation (tx={int(tx)}, ty={int(ty)})"


@daftar("Rotation", param=(-360, 360, 30), label="Sudut rotasi (derajat)", histogram=False)
def rotation(img, p, img2=None):
    H, W, _ = img.shape
    M = cv2.getRotationMatrix2D((W / 2.0, H / 2.0), float(p), 1.0)
    hasil = cv2.warpAffine(img, M, (W, H))
    return hasil, f"Geometrics: Rotation ({p}°)"


@daftar("Zooming", param=(10, 300, 150), label="Zoom (%)", histogram=False)
def zooming(img, p, img2=None):
    H, W, _ = img.shape
    skala = p / 100.0
    new_w, new_h = max(1, int(W * skala)), max(1, int(H * skala))
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    if skala >= 1.0:
        x1, y1 = (new_w - W) // 2, (new_h - H) // 2
        hasil = resized[y1:y1 + H, x1:x1 + W]
    else:
        hasil = np.zeros_like(img)
        x1, y1 = (W - new_w) // 2, (H - new_h) // 2
        hasil[y1:y1 + new_h, x1:x1 + new_w] = resized
    return hasil, f"Geometrics: Zooming ({skala:.2f}x)"


@daftar("Flipping", param=(0, 2, 0), label="Mode (0=Horizontal, 1=Vertikal, 2=Keduanya)", histogram=False)
def flipping(img, p, img2=None):
    kode, nama = {0: (1, "Horizontal"), 1: (0, "Vertikal")}.get(p, (-1, "Horizontal + Vertikal"))
    return cv2.flip(img, kode), f"Geometrics: Flipping ({nama})"


@daftar("Cropping", param=(5, 220, 40), label="Besar pemotongan tepi", histogram=False)
def cropping(img, p, img2=None):
    H, W, _ = img.shape
    rasio = min(max(p, 5), 220) / 512.0
    dx, dy = int(W * rasio), int(H * rasio)
    hasil = img[dy:max(dy + 1, H - dy), dx:max(dx + 1, W - dx)]
    return hasil, "Geometrics: Cropping"


# ---------------- Thresholding ----------------
@daftar("Thresholding", param=(0, 255, 128), label="Nilai ambang (T)", histogram=True)
def thresholding(img, p, img2=None):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, p, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB), f"Thresholding (T={p})"


# ---------------- Convolution ----------------
@daftar("Convolution", param=(0, 2, 0), label="Kernel (0=Smoothing, 1=Sharpening, 2=Edge)", histogram=False)
def convolution(img, p, img2=None):
    if p == 0:
        kernel = np.ones((5, 5), np.float32) / 25.0
        nama = "Averaging / Smoothing 5x5"
    elif p == 1:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        nama = "Sharpening 3x3"
    else:
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
        nama = "Edge Kernel 3x3"
    return cv2.filter2D(img, -1, kernel), f"Convolution ({nama})"


# ---------------- Fourier Transform ----------------
@daftar("Fourier Transform", histogram=False)
def fourier(img, p, img2=None):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    mag = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
    mag_norm = cv2.normalize(cv2.log(mag + 1.0), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    return cv2.cvtColor(mag_norm, cv2.COLOR_GRAY2RGB), "Fourier Transform"
