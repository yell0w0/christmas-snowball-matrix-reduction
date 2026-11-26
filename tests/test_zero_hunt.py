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
    # game window: when the run ends (30th zero + 1.5) the top of the screen is still on the map
    sled_y_px, px = 392, meta["art_scale"]
    assert zs[29] + 1.5 + sled_y_px / (meta["art_px_per_t"] * px) <= meta["t_max"]


def test_terrain_assets_match_metadata_and_peaks_sit_on_zeros():
    from PIL import Image
    meta = json.load(open(os.path.join(ROOT, "zero_hunt", "map_meta.json")))
    comp = os.path.join(ROOT, "zero_hunt", "component")
    for name in ("terrain.png", "height.png"):
        assert Image.open(os.path.join(comp, name)).size == (meta["width"], meta["height"])
    hm = np.asarray(Image.open(os.path.join(comp, "height.png")), dtype=float)
    col = int((0.5 - meta["sigma_min"]) * meta["art_px_per_sigma"])
    for z in meta["zeros"][:30]:
        row = int((meta["t_max"] - z) * meta["art_px_per_t"])
        # the summit plateau near each zero is centred (within ~1 pixel) on the zero
        win = hm[row - 6: row + 7, col - 6: col + 7]
        rs, cs = np.nonzero(win == win.max())
        assert win.max() >= 230  # near the clipped summit height
        assert abs(rs.mean() - 6) <= 1.5 and abs(cs.mean() - 6) <= 1.5
