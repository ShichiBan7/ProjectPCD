"""Colouring: Binary, Grayscale, RGB, HSV, CMY, YUV, YIQ, Pseudo."""
import numpy as np
import cv2
from . import daftar


@daftar("Grayscale", histogram=True)
def grayscale(img, p, img2=None):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB), "Colouring: Grayscale"


@daftar("Binary", param=(0, 255, 128), label="Nilai ambang (T)", histogram=True)
def binary(img, p, img2=None):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, biner = cv2.threshold(gray, p, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(biner, cv2.COLOR_GRAY2RGB), f"Colouring: Binary (T={p})"


@daftar("RGB", param=(0, 2, 0), label="Kanal (0=Red, 1=Green, 2=Blue)", histogram=True)
def rgb(img, p, img2=None):
    r, g, b = cv2.split(img)
    nol = np.zeros_like(r)
    if p == 0:
        hasil, kanal = cv2.merge([r, nol, nol]), "Red Channel"
    elif p == 1:
        hasil, kanal = cv2.merge([nol, g, nol]), "Green Channel"
    else:
        hasil, kanal = cv2.merge([nol, nol, b]), "Blue Channel"
    return hasil, f"Colouring: RGB ({kanal})"


@daftar("HSV", histogram=False)
def hsv(img, p, img2=None):
    return cv2.cvtColor(img, cv2.COLOR_RGB2HSV), "Colouring: HSV"


@daftar("CMY", histogram=False)
def cmy(img, p, img2=None):
    # CMY = 255 - RGB, sehingga secara hitungan sama dengan Negative.
    return 255 - img, "Colouring: CMY (255 - RGB)"


@daftar("YUV", histogram=False)
def yuv(img, p, img2=None):
    return cv2.cvtColor(img, cv2.COLOR_RGB2YUV), "Colouring: YUV"


@daftar("YIQ", histogram=False)
def yiq(img, p, img2=None):
    mat = np.array([[0.299, 0.587, 0.114],
                    [0.596, -0.274, -0.322],
                    [0.211, -0.523, 0.312]], dtype=np.float32)
    hasil = cv2.transform(img.astype(np.float32), mat)
    hasil[:, :, 1:] += 128.0
    return cv2.convertScaleAbs(np.clip(hasil, 0, 255)), "Colouring: YIQ"


@daftar("Pseudo", param=(0, 3, 0), label="Colormap (0=Jet, 1=Hot, 2=Cool, 3=Rainbow)", histogram=False)
def pseudo(img, p, img2=None):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    peta = [cv2.COLORMAP_JET, cv2.COLORMAP_HOT, cv2.COLORMAP_COOL, cv2.COLORMAP_RAINBOW]
    bgr = cv2.applyColorMap(gray, peta[min(max(p, 0), 3)])
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), "Colouring: Pseudo"
