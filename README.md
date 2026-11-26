# 🐙 Constantine's Snowball Tensor Fight

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
