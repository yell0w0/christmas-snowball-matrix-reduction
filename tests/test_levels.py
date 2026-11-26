"""Check every level is solvable by its recipe and that the stated scores are honest."""
from fractions import Fraction
from itertools import product
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levels import LEVELS, matmul_2x2_tensor, nonzero_count  # noqa: E402


def shape(t):
    return len(t), len(t[0]), len(t[0][0])


def apply(t, u, v, w, sign=-1):
    ni, nj, nk = shape(t)
    out = [[[t[i][j][k] for k in range(nk)] for j in range(nj)] for i in range(ni)]
    for i, j, k in product(range(ni), range(nj), range(nk)):
        out[i][j][k] += sign * u[i] * v[j] * w[k]
    return out


def rank(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    r = 0
    for c in range(len(m[0]) if m else 0):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def flattening_ranks(t):
    ni, nj, nk = shape(t)
    f1 = [[t[i][j][k] for j in range(nj) for k in range(nk)] for i in range(ni)]
    f2 = [[t[i][j][k] for i in range(ni) for k in range(nk)] for j in range(nj)]
    f3 = [[t[i][j][k] for i in range(ni) for j in range(nj)] for k in range(nk)]
    return rank(f1), rank(f2), rank(f3)


def test_recipes_clear_their_boards():
    for lvl in LEVELS.values():
        t = lvl["tensor"]
        for step in lvl["recipe"]:
            t = apply(t, step["u"], step["v"], step["w"])
        assert nonzero_count(t) == 0, lvl["id"]
        assert len(lvl["recipe"]) == lvl["birdie"]


def test_par_is_one_throw_per_cell():
    for lvl in LEVELS.values():
        assert nonzero_count(lvl["tensor"]) == lvl["par"]


def test_matmul_tensor_is_the_real_one():
    t = matmul_2x2_tensor()
    a = [3, 1, 4, 1]  # a11 a12 a21 a22
    b = [5, 9, 2, 6]
    c = [sum(a[i] * b[j] * t[i][j][k] for i in range(4) for j in range(4)) for k in range(4)]
    assert c == [3 * 5 + 1 * 2, 3 * 9 + 1 * 6, 4 * 5 + 1 * 2, 4 * 9 + 1 * 6]


def test_speedrun_birdie_is_provably_optimal():
    # tensor rank >= every flattening rank
    assert max(flattening_ranks(LEVELS["speedrun"]["tensor"])) == LEVELS["speedrun"]["birdie"]


def test_ranks_cover_all_scores():
    for lvl in LEVELS.values():
        assert lvl["ranks"][-1]["max"] >= 99
