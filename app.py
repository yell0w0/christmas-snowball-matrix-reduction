"""Constantine's Snowball Tensor Fight — Octopus Energy Data Advent.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from levels import LEVELS

st.set_page_config(
    page_title="Constantine's Snowball Tensor Fight",
    page_icon="🐙",
    layout="centered",
)

# The game is a single self-contained HTML5 canvas + vanilla JS file.  It's
# loaded as a (build-free) bidirectional component so the game can hand the
# finished scorecard back to Streamlit.
_game = components.declare_component(
    "snowball_tensor", path=str(Path(__file__).parent / "snowball_tensor")
)

# ----------------------------------------------------------------- theme
st.markdown(
    """
<style>
  :root { --bg:#10002B; --card:#1D0042; --pink:#F050F8; --cyan:#00F0FF; --text:#FFFFFF; }
  .stApp { background: radial-gradient(1200px 600px at 50% -10%, #2A0060 0%, #10002B 55%) fixed; color: var(--text); }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { padding-top: 2.2rem; max-width: 780px; }
  h1, h2, h3, p, li, label, span, div { color: var(--text); }
  .hero h1 { font-size: 2.15rem; line-height: 1.1; margin: 0; letter-spacing: -0.02em;
             text-shadow: 0 0 22px rgba(240,80,248,.65); }
  .hero .kicker { color: var(--cyan); font-weight: 800; letter-spacing: .18em; font-size: .78rem; text-transform: uppercase; }
  .hero p { color: #CDBDF0; margin: .35rem 0 0; }
  .pill { display:inline-block; padding: 2px 10px; border-radius: 999px; border: 1px solid var(--pink);
          color: var(--pink); font-weight: 700; font-size: .78rem; margin-right: 6px; }
  [data-testid="stExpander"] { background: var(--card); border: 1px solid #3B1670; border-radius: 14px; }
  [data-testid="stExpander"] summary:hover { color: var(--cyan); }
  [data-testid="stMetric"] { background: var(--card); border: 1px solid #3B1670; border-radius: 14px; padding: 10px 14px; }
  [data-testid="stMetricValue"] { color: var(--cyan); }
  div[role="radiogroup"] label { background: var(--card); border: 1px solid #3B1670; border-radius: 999px;
                                 padding: 4px 12px 4px 8px; margin-right: 6px; }
  div[role="radiogroup"] label:has(input:checked) { border-color: var(--pink); box-shadow: 0 0 12px rgba(240,80,248,.45); }
  .stCode, pre { border: 1px solid var(--cyan) !important; border-radius: 12px !important; }
  a { color: var(--cyan) !important; }
  .snow { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .snow i { position: absolute; top: -10px; color: #fff; opacity: .55; animation: fall linear infinite; }
  @keyframes fall { to { transform: translateY(110vh) translateX(30px); } }
  .scorecard-box { background: var(--card); border: 1px solid var(--pink); border-radius: 14px; padding: 14px 16px;
                   box-shadow: 0 0 26px rgba(240,80,248,.25); margin-bottom: .5rem; }
</style>
""",
    unsafe_allow_html=True,
)

# Falling festive snow behind the Streamlit shell (pure CSS, no JS).
_flakes = "".join(
    f'<i style="left:{(i * 37) % 100}%;font-size:{8 + (i * 7) % 10}px;'
    f'animation-duration:{9 + (i * 13) % 11}s;animation-delay:-{(i * 7) % 15}s">❄</i>'
    for i in range(28)
)
st.markdown(f'<div class="snow">{_flakes}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------- header
st.markdown(
    """
<div class="hero">
  <div class="kicker">🐙 Octopus Energy · Data Advent</div>
  <h1>Constantine's Snowball Tensor Fight</h1>
  <p>Every throw is <b>one multiplication</b>. Clear the board in fewer throws than the textbook and you've
  invented a faster matrix-multiplication algorithm — the same game AlphaTensor was trained to play.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

if "best" not in st.session_state:
    st.session_state.best = {}
if "reset_token" not in st.session_state:
    st.session_state.reset_token = 0
if "last_seen" not in st.session_state:
    st.session_state.last_seen = None

order = ["warmup", "strassen", "speedrun"]
choice = st.radio(
    "Pick your level",
    order,
    index=1,
    horizontal=True,
    format_func=lambda k: f"{LEVELS[k]['tag']}: {LEVELS[k]['title'].split(' — ')[0]}",
    label_visibility="collapsed",
)
level = LEVELS[choice]

with st.expander("🎮 How to play (30 seconds)", expanded=False):
    st.markdown(
        f"""
1. **Rows** (left, `{level['rows'][0]}`…) choose which entries of **A** go into the bracket on the left.
   **Columns** (top) do the same for **B**. Click a switch to cycle **off → + → −**.
2. The **🎁 stockings** under each board say which output entry receives the product (and with what sign).
3. **Hold** the big button (or **Space**) to charge. Watch the preview badges — then release to throw.
   Every cell where an armed row, column and stocking meet gets hit.
4. ❄️ snowballs knock **+1 → 0**. 🔥 magma balls flip the whole throw's sign.
5. Clear every cell. One cell per throw is always possible (that's *par*). Fewer throws = a genuinely
   faster algorithm. Stuck? The 🧝 elf will set the switches for the record-holding recipe.
"""
    )

# ----------------------------------------------------------------- the game
result = _game(
    level=level,
    reset_token=st.session_state.reset_token,
    key="snowball_game",
    default=None,
)

# ----------------------------------------------------------------- scorecard (shell side)
if result and result.get("at") != st.session_state.last_seen:
    st.session_state.last_seen = result.get("at")
    lvl = result["level"]
    prev = st.session_state.best.get(lvl)
    if prev is None or (result["throws"], result["seconds"]) < (prev["throws"], prev["seconds"]):
        st.session_state.best[lvl] = result
    if result["throws"] <= LEVELS[lvl]["birdie"]:
        st.balloons()

if result:
    st.markdown("#### 📣 Your Slack scorecard")
    st.caption("Hit the copy icon in the corner of the box, then paste into the Data Advent channel.")
    st.code(result["scorecard"], language=None)
    # Browsers only allow clipboard writes from a click inside the same frame, so the
    # button lives in its own tiny HTML snippet rather than being an st.button.
    components.html(
        f"""
<button id="b">📋 Copy Slack Scorecard</button>
<style>
  body {{ margin: 0; font-family: Inter, system-ui, sans-serif; }}
  #b {{ width: 100%; padding: 11px; border-radius: 999px; border: 0; background: #F050F8; color: #10002B;
        font-weight: 800; font-size: 15px; cursor: pointer; box-shadow: 0 0 18px rgba(240,80,248,.5); }}
  #b:hover {{ filter: brightness(1.1); }}
</style>
<script>
  const t = {json.dumps(result["scorecard"])};
  const b = document.getElementById("b");
  b.onclick = async () => {{
    let ok = false;
    try {{ await navigator.clipboard.writeText(t); ok = true; }} catch (e) {{}}
    if (!ok) {{
      const ta = document.createElement("textarea"); ta.value = t; document.body.appendChild(ta); ta.select();
      try {{ ok = document.execCommand("copy"); }} catch (e) {{}}
      ta.remove();
    }}
    b.textContent = ok ? "✅ Copied — paste it in Slack!" : "Use the copy icon on the box above ☝️";
    setTimeout(() => b.textContent = "📋 Copy Slack Scorecard", 2500);
  }};
</script>""",
        height=50,
    )

if st.session_state.best:
    st.markdown("#### 🏆 Your best runs this session")
    cols = st.columns(len(order))
    for col, key in zip(cols, order):
        best = st.session_state.best.get(key)
        with col:
            st.metric(
                LEVELS[key]["tag"],
                f"{best['throws']} throws" if best else "—",
                f"{best['seconds']:.1f}s · {best['rank']}" if best else None,
                delta_color="off",
            )

# ----------------------------------------------------------------- the maths
with st.expander("🤓 Wait, what's the 1969 & 2026 maths behind this?"):
    st.markdown(
        r"""
### Each throw is one multiplication

Multiplying two 2×2 matrices, $C = AB$, the textbook way needs **8** multiplications:

$$
\begin{aligned}
C_{11} &= a_{11}b_{11} + a_{12}b_{21} & C_{12} &= a_{11}b_{12} + a_{12}b_{22} \\
C_{21} &= a_{21}b_{11} + a_{22}b_{21} & C_{22} &= a_{21}b_{12} + a_{22}b_{22}
\end{aligned}
$$

Write down a 1 for every (A-entry, B-entry, C-entry) triple that appears above and you get a 4×4×4 cube of
numbers: the **matrix multiplication tensor**. That's the board — four 4×4 slices, one per output
$C_{11}, C_{12}, C_{21}, C_{22}$, each with two snowdrifts.

A throw arms some rows (a sum of A entries, $u$), some columns (a sum of B entries, $v$) and some 🎁 stockings
(where the product gets added, $w$). It costs **one** multiplication,
$m = (u \cdot a)\,(v \cdot b)$, and it hits every cell where they cross — mathematically it subtracts the
**rank-1 outer product** $u \otimes v \otimes w$ from the board. Additions and subtractions are free; only the
multiplications count, because for big matrices the "numbers" being multiplied are themselves huge
matrix blocks.

**Clear the board in _r_ throws ⇔ you've found a recipe for multiplying matrices with _r_ multiplications.**
The smallest possible _r_ is called the tensor's **rank**.

### 1969: Volker Strassen breaks the 8 barrier

Everyone assumed 8 was the minimum. Strassen found 7:

| Throw | Multiplication | Delivered to |
|---|---|---|
| M1 | $(a_{11}+a_{22})(b_{11}+b_{22})$ | $+C_{11},\ +C_{22}$ |
| M2 | $(a_{21}+a_{22})\,b_{11}$ | $+C_{21},\ -C_{22}$ |
| M3 | $a_{11}(b_{12}-b_{22})$ | $+C_{12},\ +C_{22}$ |
| M4 | $a_{22}(b_{21}-b_{11})$ | $+C_{11},\ +C_{21}$ |
| M5 | $(a_{11}+a_{12})\,b_{22}$ | $-C_{11},\ +C_{12}$ |
| M6 | $(a_{21}-a_{11})(b_{11}+b_{12})$ | $+C_{22}$ |
| M7 | $(a_{12}-a_{22})(b_{21}+b_{22})$ | $+C_{11}$ |

Notice the trick: some throws deliberately *create* mess (drifts or slush pits) that a later throw cancels.
Saving one multiplication sounds tiny, but apply it recursively to blocks of a big matrix and the cost
drops from $n^3$ to about $n^{2.81}$. In 1971 Winograd (and independently Hopcroft & Kerr) proved
**7 is the minimum** for 2×2 — so on Level 1, 7 throws is a perfect game.

The **warm-up** is the same idea one size down: Gauss noticed $(a+bi)(c+di)$ needs only 3 real
multiplications, not 4.

### From 1969 to AlphaTensor and the 2020s

Finding these recipes is a search over an astronomically large space of possible throws. In **2022 DeepMind's
AlphaTensor** turned exactly this into a single-player game ("TensorGame": pick $u, v, w$, subtract, repeat
until zero) and trained an AlphaZero-style agent to play it. It rediscovered Strassen, found a
**47-multiplication** method for 4×4 matrices in arithmetic mod 2 (beating the 49 you get from applying
Strassen twice), and improved records for several other sizes.

Since then the race has kept going: human-computer "flip graph" searches, AI systems such as DeepMind's
**AlphaEvolve (2025)**, which found a **48-multiplication** recipe for 4×4 complex matrices, and a steady stream
of newer machine-found schemes. The game you just played is the same game — just small enough to win before
your mince pie goes cold.

### 2026: OpenAI goes after the big number, ω

Strassen's trick, applied recursively, gives an algorithm costing about $n^{\omega}$ operations. The
**matrix multiplication exponent ω** is the best power achievable *as matrices get huge*. The textbook gives
3, Strassen gives 2.81, and decades of work had crept down to roughly **2.371**. Nobody can go below 2,
because you have to at least read all $n^2$ numbers.

- **October 2026:** an OpenAI preprint claimed **ω ≤ 9/4 = 2.25** — the biggest drop in decades — and shipped
  a **Lean** (machine-checked) formalisation alongside it. Academic groups have since written independent
  expositions of the proof.
- **November 2026:** a follow-up OpenAI preprint claims a **matching lower bound**, which would make
  **ω exactly 9/4**. That lower bound is for a specific model of computation (formal arithmetic circuits
  counting multiplication/division gates), and at the time of writing it is **not yet peer reviewed or
  independently checked**.

How does that connect to snowballs? The asymptotic results are still built from tensors and rank-1 pieces,
just with huge tensors and "border rank" (getting arbitrarily close to zero rather than exactly zero) instead
of exact clears on a tiny board. Strassen's 7 and the new 9/4 are the same story told at two very different
scales.

### Level 2: why is 4 *provably* optimal?

Squash the 3-D board flat three different ways (A×(B,C), B×(A,C), C×(A,B)). Each throw can raise the
ordinary matrix rank of each squashed board by at most 1. All three squashings of Level 2 have rank 4, so
**no 3-throw solution can exist** — and there's a 4-throw one hiding in there. Lower-bound arguments like this
are how mathematicians prove a record can't be beaten.
"""
    )

st.caption(
    "Built with Streamlit + one HTML5 canvas. Board maths is unit-tested — every level's record recipe "
    "really does clear its board. ❄️"
)
