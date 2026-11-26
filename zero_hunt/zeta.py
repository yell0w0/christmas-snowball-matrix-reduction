"""Riemann zeta maths for Zero Hunt.

`zeta_grid` evaluates ζ(s) on a whole numpy grid at once with Euler–Maclaurin
summation (stable in double precision for the heights we use, |t| < ~150).
`domain_colour` turns those values into the festive phase portrait the player
hunts on: every zero is a point where all the colours meet.
"""

from __future__ import annotations

from math import factorial

import numpy as np

# Bernoulli numbers B_2, B_4, ..., B_16
_B2K = [1 / 6, -1 / 30, 1 / 42, -1 / 30, 5 / 66, -691 / 2730, 7 / 6, -3617 / 510]

# Map extent (in the complex plane).  The game reads these too, via MAP_META.
SIGMA_MIN, SIGMA_MAX = -1.0, 2.0
T_MIN, T_MAX = -3.0, 116.0
PX_PER_SIGMA = 150  # horizontal pixels per unit of Re(s)
PX_PER_T = 47       # vertical pixels per unit of Im(s)


def zeta_grid(s: np.ndarray, n_terms: int = 40, k_terms: int = 8) -> np.ndarray:
    """ζ(s) for an array of complex s with 0 < |Im s| or Re s != 1 (pole at s = 1)."""
    s = np.asarray(s, dtype=np.complex128)
    N = n_terms
    total = np.zeros_like(s)
    for n in range(1, N):
        total += np.exp(-s * np.log(n))
    nlog = np.log(N)
    total += np.exp((1 - s) * nlog) / (s - 1)
    total += 0.5 * np.exp(-s * nlog)
    # Bernoulli tail: B_2k/(2k)! * s(s+1)...(s+2k-2) * N^(-s-2k+1)
    rising = s.copy()  # s(s+1)...(s+2k-2) for k = 1
    for k, b in enumerate(_B2K[:k_terms], start=1):
        if k > 1:
            rising = rising * (s + 2 * k - 3) * (s + 2 * k - 2)
        total += b / factorial(2 * k) * rising * np.exp((-s - 2 * k + 1) * nlog)
    return total


def _hex(c: str) -> np.ndarray:
    c = c.lstrip("#")
    return np.array([int(c[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


# Cyclic Octopus palette around the phase wheel.
PALETTE = [_hex(c) for c in ("#F050F8", "#7B2FF7", "#00F0FF", "#E8FFFF", "#FFB0FF")]


def domain_colour(z: np.ndarray) -> np.ndarray:
    """RGB uint8 image (H, W, 3) from complex values."""
    phase = (np.angle(z) / (2 * np.pi)) % 1.0
    pos = phase * len(PALETTE)
    i0 = np.floor(pos).astype(int) % len(PALETTE)
    i1 = (i0 + 1) % len(PALETTE)
    f = (pos - np.floor(pos))[..., None]
    f = f * f * (3 - 2 * f)  # smoothstep between palette stops
    pal = np.stack(PALETTE)
    rgb = pal[i0] * (1 - f) + pal[i1] * f

    mod = np.abs(z)
    # soft contour bands of log|ζ| give the map texture ...
    band = (np.log2(mod + 1e-12) % 1.0)
    shade = 0.80 + 0.20 * band
    # ... and the colours dim towards zeros so the meeting point reads as a "pinch"
    pinch = mod / (mod + 0.35)
    shade = shade * (0.35 + 0.65 * pinch)
    # fade the far left/right so the critical strip pops
    rgb = rgb * shade[..., None]
    return np.clip(rgb, 0, 255).astype(np.uint8)


def render_map() -> np.ndarray:
    w = int(round((SIGMA_MAX - SIGMA_MIN) * PX_PER_SIGMA))
    h = int(round((T_MAX - T_MIN) * PX_PER_T))
    sig = SIGMA_MIN + (np.arange(w) + 0.5) / PX_PER_SIGMA
    t = T_MAX - (np.arange(h) + 0.5) / PX_PER_T  # row 0 = top = highest t
    S = sig[None, :] + 1j * t[:, None]
    Z = zeta_grid(S)
    img = domain_colour(Z).astype(np.float64)
    # darken outside the critical strip a little
    outside = (sig < 0) | (sig > 1)
    img[:, outside] *= 0.62
    return img.astype(np.uint8)


def first_zeros(n: int) -> list[float]:
    """Imaginary parts of the first n non-trivial zeros (via mpmath)."""
    import mpmath

    mpmath.mp.dps = 20
    return [float(mpmath.zetazero(k).imag) for k in range(1, n + 1)]
