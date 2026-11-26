"""The zeta map and zero list the game uses are mathematically right."""
import json, os, sys
import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "zero_hunt"))
import zeta  # noqa: E402

mpmath = pytest.importorskip("mpmath")


def test_euler_maclaurin_matches_mpmath_across_the_map():
    rng = np.random.default_rng(0)
    pts = (rng.uniform(zeta.SIGMA_MIN, zeta.SIGMA_MAX, 60)
           + 1j * rng.uniform(2, zeta.T_MAX, 60))
    ours = zeta.zeta_grid(pts)
    for s, z in zip(pts, ours):
        ref = complex(mpmath.zeta(complex(s)))
        assert abs(z - ref) <= 1e-6 * max(1, abs(ref))


def test_committed_zeros_are_real_zeros_on_the_critical_line():
    meta = json.load(open(os.path.join(ROOT, "zero_hunt", "map_meta.json")))
    zs = meta["zeros"]
    assert len(zs) >= 30 and abs(zs[0] - 14.134725) < 1e-5
    assert all(a < b for a, b in zip(zs, zs[1:]))
    vals = zeta.zeta_grid(0.5 + 1j * np.array(zs))
    assert np.all(np.abs(vals) < 1e-4)
    # game window: 30th zero must be on the rendered map with headroom above the snowline view
    assert zs[29] + 1.5 + 574 / meta["px_per_t"] <= meta["t_max"]


def test_map_image_matches_metadata():
    from PIL import Image
    meta = json.load(open(os.path.join(ROOT, "zero_hunt", "map_meta.json")))
    im = Image.open(os.path.join(ROOT, "zero_hunt", "component", "zeta_map.jpg"))
    assert im.size == (meta["width"], meta["height"])
