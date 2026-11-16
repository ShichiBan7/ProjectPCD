"""Noise: Gaussian, Rayleigh, Erlang (Gamma), Exponential, Uniform, Impulse."""
import numpy as np
from . import daftar

_rng = np.random.default_rng()


def _tambah(img, derau):
    return np.clip(img.astype(np.float32) + derau, 0, 255).astype(np.uint8)


@daftar("Gaussian Noise", param=(1, 100, 25), label="Simpangan baku (sigma)", histogram=True)
def gaussian(img, p, img2=None):
    return _tambah(img, _rng.normal(0, p, img.shape)), f"Gaussian Noise (sigma={p})"


@daftar("Rayleigh Noise", param=(1, 100, 25), label="Parameter skala", histogram=True)
def rayleigh(img, p, img2=None):
    return _tambah(img, _rng.rayleigh(p, img.shape)), f"Rayleigh Noise (skala={p})"


@daftar("Erlang (Gamma) Noise", param=(1, 100, 20), label="Parameter skala (bentuk k=2)", histogram=True)
def erlang(img, p, img2=None):
    return _tambah(img, _rng.gamma(2, p / 2.0, img.shape)), f"Erlang/Gamma Noise (k=2, skala={p / 2.0:.1f})"


@daftar("Exponential Noise", param=(1, 100, 25), label="Parameter skala", histogram=True)
def exponential(img, p, img2=None):
    return _tambah(img, _rng.exponential(p, img.shape)), f"Exponential Noise (skala={p})"


@daftar("Uniform Noise", param=(1, 100, 40), label="Batas noise (-p sampai +p)", histogram=True)
def uniform(img, p, img2=None):
    return _tambah(img, _rng.uniform(-p, p, img.shape)), f"Uniform Noise (-{p}..+{p})"


@daftar("Impulse Noise", param=(1, 50, 10), label="Persentase piksel terkena noise (%)", histogram=True)
def impulse(img, p, img2=None):
    hasil = img.copy()
    acak = _rng.random(img.shape[:2])
    hasil[acak < p / 200.0] = 0          # pepper
    hasil[acak > 1 - p / 200.0] = 255    # salt
    return hasil, f"Impulse (Salt & Pepper, {p}%)  |  Library: numpy.random"
