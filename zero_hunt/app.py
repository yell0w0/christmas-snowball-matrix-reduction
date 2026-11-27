"""Constantine's Zero Hunt — Octopus Energy Data Advent.

Run from the repo root with:  streamlit run zero_hunt/app.py
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import scoreboard  # noqa: E402

META = json.loads((HERE / "map_meta.json").read_text())

st.set_page_config(page_title="Constantine's Zero Hunt", page_icon="❄", layout="centered")

_game = components.declare_component("zero_hunt", path=str(HERE / "component"))

st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
  :root { --bg:#04000C; --card:#0B0222; --pink:#F050F8; --cyan:#00F0FF; --text:#FFFFFF; --line:#2A0B5C; }
  .stApp { background: #04000C; color: var(--text); }
  .stApp::before { content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
    background: repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 1px, transparent 1px 3px); }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { padding-top: 2rem; max-width: 780px; }
  .pix { font-family: "Press Start 2P", ui-monospace, monospace; }
  .hero { border: 3px solid var(--pink); outline: 3px solid var(--line); outline-offset: -9px;
          background: var(--card); padding: 22px 22px 18px; margin-bottom: .4rem; }
  .hero .kicker { color: var(--cyan); font-size: .62rem; letter-spacing: .08em; }
  .hero h1 { font-size: 1.55rem; line-height: 1.35; margin: .6rem 0 .5rem; color: var(--pink);
             text-shadow: 3px 3px 0 #9A1AA4; }
  .hero p { color: #CDBDF0; margin: 0; font-size: .95rem; }
  h4 { font-family: "Press Start 2P", ui-monospace, monospace !important; font-size: .8rem !important; color: var(--cyan) !important; }
  [data-testid="stExpander"] { background: var(--card); border: 3px solid var(--line); border-radius: 0; }
  [data-testid="stExpander"] summary p { font-family: "Press Start 2P", ui-monospace, monospace; font-size: .7rem; color: var(--pink); }
  [data-testid="stMetric"] { background: var(--card); border: 3px solid var(--line); border-radius: 0; padding: 10px 14px; }
  [data-testid="stMetricLabel"] p { font-family: "Press Start 2P", ui-monospace, monospace; font-size: .55rem; color: #8A7AAE; }
  [data-testid="stMetricValue"] { font-family: "Press Start 2P", ui-monospace, monospace; font-size: 1.1rem; color: var(--cyan); }
  .stCode, pre { border: 3px solid var(--cyan) !important; border-radius: 0 !important; }
  a { color: var(--cyan) !important; }
  .timeline { border-left: 3px solid var(--pink); padding-left: 14px; margin: .4rem 0 1rem; }
  .timeline div { margin-bottom: .55rem; }
  .timeline b { color: var(--cyan); }
  table.hs { width: 100%; border-collapse: collapse; border: 3px solid var(--line); background: var(--card);
             font-family: "Press Start 2P", ui-monospace, monospace; font-size: .62rem; }
  table.hs th { color: #8A7AAE; text-align: left; padding: 10px 8px; border-bottom: 3px solid var(--line); font-weight: 400; }
  table.hs td { padding: 9px 8px; color: #FFFFFF; }
  table.hs tr:nth-child(1) td { color: #FFD166; }
  table.hs tr:nth-child(2) td, table.hs tr:nth-child(3) td { color: var(--cyan); }
  table.hs tr.me td { background: rgba(240,80,248,.25); color: #FFD166; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="kicker pix">OCTOPUS ENERGY - DATA ADVENT</div>
  <h1 class="pix">CONSTANTINE'S<br>ZERO HUNT</h1>
  <p>Mathematicians chased these zeros for 167 years. Last week a proof that they all sit on one
  line was checked by computer. Steer Connie's sledge up the snowy peaks and grab the baubles on top.<br><span style='color:#00F0FF'>Arrow keys</span> steer, boost and brake. Click the game first so it hears your keys.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

for k, v in {"last_seen": None, "last_rank": None, "last_result": None}.items():
    st.session_state.setdefault(k, v)


def _player_name() -> str:
    """Pre-fill the name box from the data app's login, when it has one."""
    try:
        u = st.user
        if u.get("is_logged_in"):
            return str(u.get("name") or str(u.get("email") or "").split("@")[0])
    except Exception:
        pass
    return ""


try:
    board = scoreboard.top(10)
    board_error = None
except Exception as exc:  # storage unavailable: the game still plays, board just stays empty
    board, board_error = [], str(exc)

result = _game(
    meta=META,
    leaderboard=board,
    last=st.session_state.last_rank,
    player_name=_player_name(),
    key="zero_hunt",
    default=None,
)

if result and result.get("run_id") and (result["run_id"], result.get("type")) != st.session_state.last_seen:
    st.session_state.last_seen = (result["run_id"], result.get("type"))
    st.session_state.last_result = result
    if result.get("type") == "submit":
        try:
            rank = scoreboard.submit(result)
        except Exception as exc:
            rank = None
            st.toast(f"Couldn't save to the scoreboard: {exc}")
        st.session_state.last_rank = {"run_id": result["run_id"], "rank": rank}
        st.rerun()  # hand the fresh board and the player's rank straight back to the game

last = st.session_state.last_result
if last:
    card = last["scorecard"]
    lr = st.session_state.last_rank
    if lr and lr.get("run_id") == last["run_id"] and lr.get("rank") and "global board" not in card:
        first, _, rest = card.partition("\n")
        card = f"{first} | #{lr['rank']} on the global board\n{rest}"
    st.markdown("#### SLACK SCORECARD")
    st.caption("Hit the copy icon on the box, or the big button, then paste into the Data Advent channel.")
    st.code(card, language=None)
    components.html(
        f"""
<button id="b">COPY SLACK SCORECARD</button>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
  body {{ margin: 0; }}
  #b {{ width: 100%; padding: 12px; border-radius: 0; border: 3px solid #FFFFFF; background: #F050F8; color: #04000C;
        font-family: "Press Start 2P", ui-monospace, monospace; font-size: 11px; cursor: pointer; }}
  #b:hover {{ background: #00F0FF; }}
</style>
<script>
  const t = {json.dumps(card)};
  const b = document.getElementById("b");
  b.onclick = async () => {{
    let ok = false;
    try {{ await navigator.clipboard.writeText(t); ok = true; }} catch (e) {{}}
    if (!ok) {{ const ta = document.createElement("textarea"); ta.value = t; document.body.appendChild(ta); ta.select();
      try {{ ok = document.execCommand("copy"); }} catch (e) {{}} ta.remove(); }}
    b.textContent = ok ? "COPIED! PASTE IT IN SLACK" : "USE THE COPY ICON ON THE BOX ABOVE";
    setTimeout(() => b.textContent = "COPY SLACK SCORECARD", 2500);
  }};
</script>""",
        height=50,
    )

st.markdown("#### GLOBAL HIGH SCORES")
if board_error:
    st.caption(f"Scoreboard storage unavailable ({board_error}).")
elif not board:
    st.caption("No scores yet. Be the first name on the board.")
else:
    mine = st.session_state.last_rank["run_id"] if st.session_state.last_rank else None
    rows = "".join(
        f"<tr class='{'me' if r['run_id'] == mine else ''}'><td>{i + 1}</td><td>{html.escape(r['name'])}</td>"
        f"<td>{r['score']:,}</td><td>{r['caught']}/30</td><td>{r['perfect']}</td><td>{r['falls']}</td>"
        f"<td>{int(r['seconds'] // 60)}:{int(r['seconds'] % 60):02d}</td></tr>"
        for i, r in enumerate(board)
    )
    st.markdown(
        "<table class='hs'><thead><tr><th>#</th><th>NAME</th><th>SCORE</th><th>BAUBLES</th>"
        f"<th>PERFECT</th><th>FALLS</th><th>TIME</th></tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )

with st.expander("WHAT ARE THESE ZEROS? WHAT HAPPENED LAST WEEK?"):
    st.markdown(
        r"""
### The function on the map

The **Riemann zeta function** starts life as a simple infinite sum,

$$\zeta(s) = 1 + \frac{1}{2^s} + \frac{1}{3^s} + \frac{1}{4^s} + \cdots$$

and Euler showed it secretly encodes the primes:
$\zeta(s) = \prod_p \frac{1}{1 - p^{-s}}$. Riemann (1859) extended it to complex inputs
$s = \sigma + it$. The map shows that complex plane: left–right is $\sigma$ (the real part),
up is $t$.

In the game the terrain height is $-\log|\zeta(s)|$, so wherever $\zeta(s) = 0$ the snow piles up into an
infinitely tall **peak**: every summit you race up is a **zero**. The slopes that shove your sledge around are the
real gradient of $|\zeta|$.
Besides some boring "trivial" zeros at $-2, -4, -6, \dots$, all the interesting zeros live in the
**critical strip** $0 < \sigma < 1$ (between the faint pink dots).

### The Riemann hypothesis

> Every non-trivial zero lies exactly on the line $\sigma = \tfrac12$.

That's the dotted cyan line Constantine races up. Computers had checked trillions of zeros, and every one was on
the line, but checking examples isn't a proof. It's the most famous open problem in mathematics and one of
the $1M Clay Millennium Prize problems.

### Why anyone cares: zeros are the frequencies of the primes

Riemann's **explicit formula** writes the prime-counting staircase as a smooth trend *plus one wave per zero*.
The height $t$ of a zero sets the wave's frequency, and its real part $\sigma$ sets how loud the wave grows.
If every zero sits at $\sigma = \tfrac12$, all the waves are as quiet as possible, which means **the primes are
spread out as regularly as they possibly could be**. Mathematicians would call it a Fourier decomposition of the
primes, with the hypothesis bounding the noise. Prime-counting estimates, some cryptography arguments and many
algorithm analyses lean on it. *(Act 2 will let you see this: your baubles' waves light up the prime
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

The terrain was computed for this game in Python. It evaluates ζ on a 150 × 1,936 pixel-art grid with
Euler–Maclaurin summation (accurate to better than $10^{-6}$, tested against `mpmath`), then draws
snow-band contours of $-\log|\zeta|$. The game reads the same heightmap for its sledge physics. The 30 zeros you
hunt are the true first 30, from $t \approx 14.13$ up to $t \approx 101.32$, found with `mpmath.zetazero`.
"""
        ,
        unsafe_allow_html=True,
    )

st.caption(
    "Sources: Anthropic research (Aug 2026), Quanta (Oct 2026), Scientific American & the Waterloo verification "
    "page (Nov 2026). Built with Streamlit, numpy, mpmath and one HTML5 canvas."
)
