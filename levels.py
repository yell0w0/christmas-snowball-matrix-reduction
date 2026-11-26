"""Level definitions for Constantine's Snowball Tensor Fight.

Every level is a 3-D tensor T[i][j][k]:
    i -> an entry of the left input  (row switches,  "A ingredients")
    j -> an entry of the right input (column switches, "B ingredients")
    k -> an entry of the output      (stocking switches, "C outputs")

A throw is a rank-1 tensor  u ⊗ v ⊗ w  with u, v, w in {-1, 0, +1}.
Snowball mode subtracts it from the board, Magma mode adds it.
The board is cleared when every cell is 0, i.e. when the throws you made sum
to the original tensor: that *is* a multiplication algorithm using one
multiplication per throw.

Each level's `recipe` is a known optimal solution (checked in tests).
"""

from __future__ import annotations

from itertools import product


def matmul_2x2_tensor() -> list[list[list[int]]]:
    """The 2x2 matrix multiplication tensor: c_rc = sum_k a_rk * b_kc."""
    t = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    for r, k, c in product(range(2), repeat=3):
        t[r * 2 + k][k * 2 + c][r * 2 + c] = 1
    return t


def complex_mult_tensor() -> list[list[list[int]]]:
    """(a + bi)(c + di) = (ac - bd) + (ad + bc)i."""
    t = [[[0] * 2 for _ in range(2)] for _ in range(2)]
    t[0][0][0] = 1   # ac  -> Re
    t[1][1][0] = -1  # -bd -> Re
    t[0][1][1] = 1   # ad  -> Im
    t[1][0][1] = 1   # bc  -> Im
    return t


def tensor_from_recipe(recipe, shape) -> list[list[list[int]]]:
    ni, nj, nk = shape
    t = [[[0] * nk for _ in range(nj)] for _ in range(ni)]
    for step in recipe:
        u, v, w = step["u"], step["v"], step["w"]
        for i, j, k in product(range(ni), range(nj), range(nk)):
            t[i][j][k] += u[i] * v[j] * w[k]
    return t


A4 = ["a₁₁", "a₁₂", "a₂₁", "a₂₂"]
B4 = ["b₁₁", "b₁₂", "b₂₁", "b₂₂"]
C4 = ["C₁₁", "C₁₂", "C₂₁", "C₂₂"]

# Strassen (1969).  M1..M7, each delivered to the C entries in w.
STRASSEN = [
    {"name": "M1", "u": [1, 0, 0, 1],  "v": [1, 0, 0, 1],  "w": [1, 0, 0, 1]},
    {"name": "M2", "u": [0, 0, 1, 1],  "v": [1, 0, 0, 0],  "w": [0, 0, 1, -1]},
    {"name": "M3", "u": [1, 0, 0, 0],  "v": [0, 1, 0, -1], "w": [0, 1, 0, 1]},
    {"name": "M4", "u": [0, 0, 0, 1],  "v": [-1, 0, 1, 0], "w": [1, 0, 1, 0]},
    {"name": "M5", "u": [1, 1, 0, 0],  "v": [0, 0, 0, 1],  "w": [-1, 1, 0, 0]},
    {"name": "M6", "u": [-1, 0, 1, 0], "v": [1, 1, 0, 0],  "w": [0, 0, 0, 1]},
    {"name": "M7", "u": [0, 1, 0, -1], "v": [0, 0, 1, 1],  "w": [1, 0, 0, 0]},
]

GAUSS = [
    {"name": "k1", "u": [1, 1], "v": [1, 0],  "w": [1, 1]},   # c(a+b) -> Re, Im
    {"name": "k2", "u": [1, 0], "v": [-1, 1], "w": [0, 1]},   # a(d-c) -> Im
    {"name": "k3", "u": [0, 1], "v": [1, 1],  "w": [-1, 0]},  # b(c+d) -> -Re
]

# A 4-term "sub-tensor" on the same 4x4x4 board.  All three flattenings have
# rank 4, so no 3-throw solution exists: 4 is provably optimal.
SPEEDRUN = [
    {"name": "S1", "u": [0, 0, 0, 1], "v": [0, 0, 1, 0],  "w": [0, 0, 1, 1]},
    {"name": "S2", "u": [0, 1, 0, 1], "v": [1, 0, 0, 1],  "w": [-1, 0, 0, 0]},
    {"name": "S3", "u": [0, 0, 1, 1], "v": [0, 0, 0, -1], "w": [-1, 0, 0, -1]},
    {"name": "S4", "u": [1, 0, 0, 0], "v": [0, 1, 0, 1],  "w": [1, 1, 0, 0]},
]

LEVELS: dict[str, dict] = {
    "warmup": {
        "id": "warmup",
        "tag": "Warm-up",
        "title": "Gauss's Complex Trick",
        "blurb": "Multiply (a + bi)(c + di). Textbook needs 4 multiplications; Gauss needed 3.",
        "rows": ["a", "b"],
        "cols": ["c", "d"],
        "layers": ["Re", "Im"],
        "tensor": complex_mult_tensor(),
        "par": 4,
        "birdie": 3,
        "birdie_label": "Gauss",
        "recipe": GAUSS,
        "ranks": [
            {"max": 3, "title": "Gauss Mode Unlocked", "brag": "Beat the textbook!"},
            {"max": 4, "title": "Textbook Elf", "brag": "Par"},
            {"max": 99, "title": "Enthusiastic Snowman", "brag": "Snow way!"},
        ],
    },
    "strassen": {
        "id": "strassen",
        "tag": "Level 1",
        "title": "2×2 Classic — Beat Strassen 1969",
        "blurb": "Clear the 2×2 matrix-multiplication tensor. Naive = 8 throws. Strassen did it in 7.",
        "rows": A4,
        "cols": B4,
        "layers": C4,
        "tensor": matmul_2x2_tensor(),
        "par": 8,
        "birdie": 7,
        "birdie_label": "Strassen",
        "recipe": STRASSEN,
        "ranks": [
            {"max": 7, "title": "Strassen Grandmaster", "brag": "Beat 1969!"},
            {"max": 8, "title": "Textbook Elf", "brag": "Matched the 1968 textbook"},
            {"max": 10, "title": "Snowball Enthusiast", "brag": "Got there!"},
            {"max": 99, "title": "Blizzard Survivor", "brag": "Survived the blizzard"},
        ],
    },
    "speedrun": {
        "id": "speedrun",
        "tag": "Level 2",
        "title": "2026 Speedrun — Sub-Tensor Challenge",
        "blurb": "9 snowdrifts, 3 slush pits. Naive = 12 throws. The provable minimum is 4. Clock's ticking.",
        "rows": A4,
        "cols": B4,
        "layers": C4,
        "tensor": tensor_from_recipe(SPEEDRUN, (4, 4, 4)),
        "par": 12,
        "birdie": 4,
        "birdie_label": "Proven optimal",
        "recipe": SPEEDRUN,
        "ranks": [
            {"max": 4, "title": "AlphaTensor Mode", "brag": "Provably optimal!"},
            {"max": 7, "title": "2026 Speedrunner", "brag": "Big speedrun energy"},
            {"max": 11, "title": "Sub-Tensor Scrapper", "brag": "Beat naive!"},
            {"max": 99, "title": "Naive Elf", "brag": "One flake at a time"},
        ],
    },
}


def nonzero_count(t) -> int:
    return sum(1 for plane in t for row in plane for x in row if x)
