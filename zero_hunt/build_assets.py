"""Regenerate the static assets the game loads (outputs are committed).

    python zero_hunt/build_assets.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

import zeta

OUT = Path(__file__).parent / "component"


def main() -> None:
    hgt = zeta.terrain_heights()
    Image.fromarray(zeta.terrain_image(hgt)).save(OUT / "terrain.png", optimize=True)
    q = np.round((hgt - zeta.H_MIN) / (zeta.H_MAX - zeta.H_MIN) * 255).astype(np.uint8)
    Image.fromarray(q, mode="L").save(OUT / "height.png", optimize=True)
    zeros = [z for z in zeta.first_zeros(40) if z < zeta.ART_T_MAX - 4]
    meta = {
        "sigma_min": zeta.SIGMA_MIN,
        "sigma_max": zeta.SIGMA_MAX,
        "t_min": zeta.ART_T_MIN,
        "t_max": zeta.ART_T_MAX,
        "art_scale": zeta.ART_SCALE,
        "art_px_per_t": zeta.ART_PX_PER_T,
        "art_px_per_sigma": zeta.ART_PX_PER_SIGMA,
        "h_min": zeta.H_MIN,
        "h_max": zeta.H_MAX,
        "width": int(hgt.shape[1]),
        "height": int(hgt.shape[0]),
        "zeros": [round(z, 6) for z in zeros],
    }
    (Path(__file__).parent / "map_meta.json").write_text(json.dumps(meta, indent=1))
    print(f"terrain {hgt.shape[1]}x{hgt.shape[0]} art px, {len(zeros)} zeros up to t={zeros[-1]:.3f}")


if __name__ == "__main__":
    main()
