"""Constantine's Zero Hunt — Octopus Energy Data Advent.

Run from the repo root with:  streamlit run zero_hunt/app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent
META = json.loads((HERE / "map_meta.json").read_text())

st.set_page_config(page_title="Constantine's Zero Hunt", page_icon="🐙", layout="centered")

_game = components.declare_component("zero_hunt", path=str(HERE / "component"))

st.markdown(
    """
<style>
  :root { --bg:#10002B; --card:#1D0042; --pink:#F050F8; --cyan:#00F0FF; --text:#FFFFFF; }
  .stApp { background: radial-gradient(1200px 600px at 50% -10%, #2A0060 0%, #10002B 55%) fixed; color: var(--text); }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { padding-top: 2.2rem; max-width: 780px; }
  .hero h1 { font-size: 2.15rem; line-height: 1.1; margin: 0; letter-spacing: -0.02em; text-shadow: 0 0 22px rgba(240,80,248,.65); }
  .hero .kicker { color: var(--cyan); font-weight: 800; letter-spacing: .18em; font-size: .78rem; text-transform: uppercase; }
  .hero p { color: #CDBDF0; margin: .35rem 0 0; }
  [data-testid="stExpander"] { background: var(--card); border: 1px solid #3B1670; border-radius: 14px; }
  [data-testid="stMetric"] { background: var(--card); border: 1px solid #3B1670; border-radius: 14px; padding: 10px 14px; }
  [data-testid="stMetricValue"] { color: var(--cyan); }
  .stCode, pre { border: 1px solid var(--cyan) !important; border-radius: 12px !important; }
  a { color: var(--cyan) !important; }
  .snow { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .snow i { position: absolute; top: -10px; color: #fff; opacity: .55; animation: fall linear infinite; }
  @keyframes fall { to { transform: translateY(110vh) translateX(30px); } }
  .timeline { border-left: 2px solid var(--pink); padding-left: 14px; margin: .4rem 0 1rem; }
  .timeline div { margin-bottom: .55rem; }
  .timeline b { color: var(--cyan); }
</style>
""",
    unsafe_allow_html=True,
)
_flakes = "".join(
    f'<i style="left:{(i * 37) % 100}%;font-size:{8 + (i * 7) % 10}px;'
    f'animation-duration:{9 + (i * 13) % 11}s;animation-delay:-{(i * 7) % 15}s">❄</i>'
    for i in range(28)
)
st.markdown(f'<div class="snow">{_flakes}</div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="hero">
  <div class="kicker">🐙 Octopus Energy · Data Advent</div>
  <h1>Constantine's Zero Hunt</h1>
  <p>Mathematicians chased these zeros for 167 years. Last week a proof that they all sit on one
  line was checked by computer. Your job: catch 30 of them before they slide past the snowline.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

if "best" not in st.session_state:
    st.session_state.best = None
if "last_seen" not in st.session_state:
    st.session_state.last_seen = None

result = _game(meta=META, key="zero_hunt", default=None)

if result and result.get("at") != st.session_state.last_seen:
    st.session_state.last_seen = result.get("at")
    best = st.session_state.best
    if best is None or result["score"] > best["score"]:
        st.session_state.best = result
    if result["caught"] == result["total"]:
        st.balloons()

if result:
    st.markdown("#### 📣 Your Slack scorecard")
    st.caption("Hit the copy icon on the box, or the big button, then paste into the Data Advent channel.")
    st.code(result["scorecard"], language=None)
    components.html(
        f"""
<button id="b">📋 Copy Slack Scorecard</button>
<style>
  body {{ margin: 0; font-family: Inter, system-ui, sans-serif; }}
  #b {{ width: 100%; padding: 11px; border-radius: 999px; border: 0; background: #F050F8; color: #10002B;
        font-weight: 800; font-size: 15px; cursor: pointer; box-shadow: 0 0 18px rgba(240,80,248,.5); }}
</style>
<script>
  const t = {json.dumps(result["scorecard"])};
  const b = document.getElementById("b");
  b.onclick = async () => {{
    let ok = false;
    try {{ await navigator.clipboard.writeText(t); ok = true; }} catch (e) {{}}
    if (!ok) {{ const ta = document.createElement("textarea"); ta.value = t; document.body.appendChild(ta); ta.select();
      try {{ ok = document.execCommand("copy"); }} catch (e) {{}} ta.remove(); }}
    b.textContent = ok ? "✅ Copied! Paste it in Slack" : "Use the copy icon on the box above ☝️";
    setTimeout(() => b.textContent = "📋 Copy Slack Scorecard", 2500);
  }};
</script>""",
        height=50,
    )

if st.session_state.best:
    b = st.session_state.best
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Best score", f"{b['score']:,}")
    c2.metric("Baubles", f"{b['caught']}/{b['total']}")
    c3.metric("Best combo", f"×{b['best_combo']}")

with st.expander("🤓 Wait, what are these zeros, and what happened last week?"):
    st.markdown(
        r"""
### The function on the map

The **Riemann zeta function** starts life as a simple infinite sum,

$$\zeta(s) = 1 + \frac{1}{2^s} + \frac{1}{3^s} + \frac{1}{4^s} + \cdots$$

and Euler showed it secretly encodes the primes:
$\zeta(s) = \prod_p \frac{1}{1 - p^{-s}}$. Riemann (1859) extended it to complex inputs
$s = \sigma + it$. The map shows that complex plane: left–right is $\sigma$ (the real part),
up is $t$. Colour shows ζ's *direction* (its phase), and the darker rings show its *size*.

A **zero** is a point where $\zeta(s) = 0$. On a colour map, every colour has to meet there, so you get a swirl.
Besides some boring "trivial" zeros at $-2, -4, -6, \dots$, all the interesting zeros live in the
**critical strip** $0 < \sigma < 1$ (the brighter band).

### The Riemann hypothesis

> Every non-trivial zero lies exactly on the line $\sigma = \tfrac12$.

That's the dashed line Constantine rides up. Computers had checked trillions of zeros, and every one was on
the line, but checking examples isn't a proof. It's the most famous open problem in mathematics and one of
the $1M Clay Millennium Prize problems.

### Why anyone cares: zeros are the frequencies of the primes 🎵

Riemann's **explicit formula** writes the prime-counting staircase as a smooth trend *plus one wave per zero*.
The height $t$ of a zero sets the wave's frequency, and its real part $\sigma$ sets how loud the wave grows.
If every zero sits at $\sigma = \tfrac12$, all the waves are as quiet as possible, which means **the primes are
spread out as regularly as they possibly could be**. Data people would call it a Fourier decomposition of the
primes, with the hypothesis bounding the noise. Prime-counting estimates, some cryptography arguments and many
algorithm analyses lean on it. *(Act 2 will let you hear and see this: your baubles' waves light up the prime
Christmas lights.)*

### 2026: the year it fell

<div class="timeline">
<div><b>Aug 2026</b> · Anthropic reported that Claude, while attempting the hypothesis, raised the proven share
of zeros on the critical line from about <b>41.6%</b> to <b>67.2%</b>, checked in Lean. That was a partial
result, not the hypothesis itself.</div>
<div><b>Oct 2026</b> · OpenAI announced a proof of a weaker <b>"quasi-Riemann hypothesis"</b>.</div>
<div><b>20 Nov 2026</b> · <b>Levent Alpöge</b> (Anthropic) announced a <b>proof of the Riemann hypothesis</b>
developed with Claude, released as a very large Lean formalisation.</div>
<div><b>21 Nov 2026</b> · The <b>Lean FRO</b> and the <b>Mathlib Initiative</b> certified that the library proves
the Riemann hypothesis exactly as Mathlib states it. Michael Rubinstein (Waterloo) separately checked the
generalised version. A much shorter Lean proof followed a few days later.</div>
</div>

**The honest caveat:** this is a machine-checked proof, so the logic has been verified by Lean's kernel,
but a human-readable write-up hasn't been published yet. Mathematicians are still digesting *why* it works.
Expect the story to keep developing.

### How the map was made

The map was computed for this game in Python. It evaluates ζ on a 450 × 5,593 grid with
Euler–Maclaurin summation (accurate to better than $10^{-7}$, tested against `mpmath`). The 30 zeros you
hunt are the true first 30, from $t \approx 14.13$ up to $t \approx 101.32$, found with `mpmath.zetazero`.
"""
        ,
        unsafe_allow_html=True,
    )

st.caption(
    "Sources: Anthropic research (Aug 2026), Quanta (Oct 2026), Scientific American & the Waterloo verification "
    "page (Nov 2026). Built with Streamlit, numpy, mpmath and one HTML5 canvas. ❄️"
)
