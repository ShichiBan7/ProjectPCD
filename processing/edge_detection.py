"""Edge Detection Segmentation: Sobel, Prewitt, Robert, Laplacian, LoG,
Canny, Compass (Kirsch)."""
import numpy as np
import cv2
from . import daftar


def _gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def _ke_rgb(peta):
    """Normalisasi ke 0-255 lalu ubah menjadi citra RGB."""
    norm = cv2.normalize(np.abs(peta), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.cvtColor(norm, cv2.COLOR_GRAY2RGB)


def _gradien(img, kx, ky):
    g = _gray(img).astype(np.float32)
    gx = cv2.filter2D(g, -1, np.array(kx, dtype=np.float32))
    gy = cv2.filter2D(g, -1, np.array(ky, dtype=np.float32))
    return _ke_rgb(cv2.magnitude(gx, gy))


@daftar("Sobel")
def sobel(img, p, img2=None):
    g = _gray(img)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    return _ke_rgb(cv2.magnitude(gx, gy)), "Sobel"


@daftar("Prewitt")
def prewitt(img, p, img2=None):
    kx = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    ky = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    return _gradien(img, kx, ky), "Prewitt"


@daftar("Robert")
def robert(img, p, img2=None):
    kx = [[1, 0], [0, -1]]
    ky = [[0, 1], [-1, 0]]
    return _gradien(img, kx, ky), "Robert (Roberts Cross)"


@daftar("Laplacian")
def laplacian(img, p, img2=None):
    lap = cv2.Laplacian(_gray(img), cv2.CV_32F, ksize=3)
    return _ke_rgb(lap), "Laplacian"


@daftar("Laplacian of Gaussian (LoG)", param=(1, 10, 2), label="Sigma Gaussian")
def log(img, p, img2=None):
    k = 2 * int(3 * p) + 1
    blur = cv2.GaussianBlur(_gray(img), (k, k), p)
    return _ke_rgb(cv2.Laplacian(blur, cv2.CV_32F, ksize=3)), f"LoG (sigma={p})"


@daftar("Canny", param=(10, 200, 80), label="Ambang bawah (ambang atas = 2x)")
def canny(img, p, img2=None):
    tepi = cv2.Canny(_gray(img), p, p * 2)
    return cv2.cvtColor(tepi, cv2.COLOR_GRAY2RGB), f"Canny ({p}, {p * 2})"


@daftar("Compass")
def compass(img, p, img2=None):
    """Kirsch: 8 arah mata angin, diambil respons terbesar."""
    g = _gray(img).astype(np.float32)
    cincin = [-3, -3, 5, 5, 5, -3, -3, -3]          # nilai di sekeliling pusat
    posisi = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]
    respons = []
    for geser in range(8):
        kernel = np.zeros((3, 3), dtype=np.float32)
        for i, (r, c) in enumerate(posisi):
            kernel[r, c] = cincin[(i - geser) % 8]
        respons.append(cv2.filter2D(g, -1, kernel))
    return _ke_rgb(np.max(respons, axis=0)), "Compass (Kirsch 8 arah)"
