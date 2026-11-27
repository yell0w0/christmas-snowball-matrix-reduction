# 🐙 Data Advent: Constantine's maths games

Two festive Streamlit mini-games for the Octopus Energy Data Advent calendar.

## Zero Hunt (Riemann hypothesis): `streamlit run zero_hunt/app.py`

An 8-bit arcade racer. The terrain is a pixel-art snow map whose height is -log|ζ(s)|, so every zeta zero is a snowy
peak, and all of them sit on the critical line Re(s) = ½ (proven in Lean in November 2026 by Alpöge & Claude). Steer
Constantine's wobbly sledge with the arrow keys (up to boost, down to brake). The real slopes of |ζ| push you around, and
you grab the bauble on each summit. You score for every bauble, for how close to the summit you pass, for combos and for
time. Music is a swing chiptune bassline over ii-V-I changes, and the catch chimes walk up and back down a Dorian scale.

* `zero_hunt/zeta.py`: vectorised Euler–Maclaurin ζ(s), plus the terrain bands and contours.
* `zero_hunt/build_assets.py`: regenerates `component/terrain.png`, `component/height.png` (the physics heightmap)
  and `map_meta.json` (needs `mpmath`). All three are committed, so the app itself needs no maths libraries at runtime.
* `zero_hunt/component/index.html`: the canvas game (sprites, physics, audio, CRT overlay).
* `zero_hunt/scoreboard.py`: the global high-score table (SQLite). Players enter a name at the end of a run and get
  ranked; the title screen cycles to the top 10 in attract mode.
  **Hosting:** set `ZERO_HUNT_DB=/path/on/shared/persistent/storage/scores.sqlite3` so the board survives restarts and
  every app replica sees the same file. Swap `submit`/`top` for your warehouse if you'd rather keep it there. If the
  data app has login (`st.user`), the name box is pre-filled from it. Scores are submitted by the browser, so treat the
  board as friendly competition rather than tamper-proof.
* Music: a small jazz trio in Web Audio (FM Rhodes with stereo tremolo, or a piano with hammer-shaped harmonics;
  upright bass; dark noise-wash ride and hi-hat; room reverb), harmonised after Jazzology (Rawlins & Bahha):
  * SWING (Rhodes): I-VI-ii-V in C (Cmaj9, A7alt, Dm9, G13, Em7). Rootless type A/B left-hand voicings that switch
    on 4th/5th root motion.
  * BLUES (piano): the book's jazz-blues in F (F13, Bb13, Cm9-F13, B°7, D7alt, Gm9, C13, Am9-D7alt, Gm9-C7alt).

  Walking bass is generated per tune: roots on changes, scale steps between, and chromatic or dominant approach notes.
  The background pianist comps with Jazzology swing rhythms and lays out while you play. **You are the comping
  pianist**: each catch ticks instantly, then lands on the next swung off-beat as a chord. That chord is the left-hand
  voicing plus a Garland-style right hand with the melody on top. GREAT doubles the melody at the octave, PERFECT fills
  in a block chord, and every fifth catch in a combo adds a crushed grace note. `__zh.renderDemo(id)` renders a tune
  offline to a WAV file.
* Tuning knobs: `cruise()`, the gravity factor (`-46 * gS`), `CATCH_R`, `GREAT_R` and `PERFECT_R` in `index.html`.

---

## ❄️ Constantine's Snowball Tensor Fight (matrix multiplication): `streamlit run app.py`

A festive Streamlit mini-game for the Octopus Energy Data Advent calendar. Every snowball throw is **one
multiplication**. Clear the board in fewer throws than the textbook and you've found a faster
matrix-multiplication algorithm. It's the same "TensorGame" that DeepMind's AlphaTensor was trained to play.

```bash
pip install -r requirements.txt
streamlit run app.py
python -m pytest -q tests   # checks every level's record recipe really clears its board
```

## Levels

| Level | Board | Par (naive) | Target |
|---|---|---|---|
| Warm-up: Gauss's Complex Trick | (a+bi)(c+di), 2×2×2 | 4 | 3 |
| Level 1: 2×2 Classic, Beat Strassen 1969 | 2×2 matmul tensor, 4×4×4 | 8 | 7 (Strassen; proven optimal) |
| Level 2: 2026 Speedrun, Sub-Tensor Challenge | 9 drifts + 3 slush pits, 4×4×4 | 12 | 4 (proven optimal via flattening rank) |

## How it's built

* `app.py`: Streamlit shell with the level picker, how-to-play, Slack scorecard with a copy button, session bests, and the maths explainer.
* `snowball_tensor/index.html`: the whole game in one self-contained HTML5 canvas + vanilla JS file, running at 60fps
  (hold-to-charge, lasers, previews, Web Audio synth, particles, Constantine). It's loaded through
  `components.declare_component(path=...)` with no build step, so the game can **send the finished scorecard back** to Streamlit.
* `levels.py`: level tensors and known optimal recipes. The game reads them from here, so there's one source of truth.

## Controls

Click row (A), column (B) and 🎁 stocking (C) switches to cycle them **off → + → −**. Hold the big button or **Space**
to charge, then release to throw. Undo, reset, 🧝 elf hint (sets the switches to the next step of the record recipe),
magma ball (flips the throw's sign), mute.
