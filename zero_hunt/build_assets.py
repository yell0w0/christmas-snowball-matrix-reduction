"""Regenerate the static assets the game loads (run once; outputs are committed).

    python zero_hunt/build_assets.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

import zeta

OUT = Path(__file__).parent / "component"


def main() -> None:
    img = zeta.render_map()
    Image.fromarray(img).save(OUT / "zeta_map.jpg", quality=86, optimize=True, progressive=True)
    zeros = [z for z in zeta.first_zeros(40) if z < zeta.T_MAX - 4]
    meta = {
        "sigma_min": zeta.SIGMA_MIN,
        "sigma_max": zeta.SIGMA_MAX,
        "t_min": zeta.T_MIN,
        "t_max": zeta.T_MAX,
        "px_per_sigma": zeta.PX_PER_SIGMA,
        "px_per_t": zeta.PX_PER_T,
        "width": img.shape[1],
        "height": img.shape[0],
        "zeros": [round(z, 6) for z in zeros],
    }
    (Path(__file__).parent / "map_meta.json").write_text(json.dumps(meta, indent=1))
    print(f"map {img.shape[1]}x{img.shape[0]}, {len(zeros)} zeros up to t={zeros[-1]:.3f}")


if __name__ == "__main__":
    main()
