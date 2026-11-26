import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "zero_hunt"))
import scoreboard  # noqa: E402


def _entry(run_id, name, score, **kw):
    e = {"run_id": run_id, "name": name, "score": score, "caught": 20, "perfect": 5, "falls": 1, "seconds": 80.5}
    e.update(kw)
    return e


def test_submit_rank_and_top(tmp_path, monkeypatch):
    monkeypatch.setenv("ZERO_HUNT_DB", str(tmp_path / "s.sqlite3"))
    assert scoreboard.submit(_entry("run_aaaaaa", "Ada", 5000)) == 1
    assert scoreboard.submit(_entry("run_bbbbbb", "Bob", 9000)) == 1
    assert scoreboard.submit(_entry("run_cccccc", "Cy", 7000)) == 2
    assert scoreboard.rank_of("run_aaaaaa") == 3
    assert [r["name"] for r in scoreboard.top()] == ["BOB", "CY", "ADA"]


def test_submit_is_idempotent_per_run(tmp_path, monkeypatch):
    monkeypatch.setenv("ZERO_HUNT_DB", str(tmp_path / "s.sqlite3"))
    scoreboard.submit(_entry("run_dddddd", "Dee", 100))
    scoreboard.submit(_entry("run_dddddd", "Dee", 99999))
    assert scoreboard.count() == 1 and scoreboard.top()[0]["score"] == 100


def test_input_is_sanitised(tmp_path, monkeypatch):
    monkeypatch.setenv("ZERO_HUNT_DB", str(tmp_path / "s.sqlite3"))
    assert scoreboard.clean_name("  <script>alert(1)</script>   ") == "SCRIPTALERT1SCRI"
    assert scoreboard.clean_name("") == "ANON"
    assert scoreboard.clean_name("connie   the\toctopus") == "CONNIE THE OCTOP"
    assert scoreboard.submit(_entry("bad id!", "x", 1)) is None
    scoreboard.submit(_entry("run_eeeeee", "Eve", 10**9, caught=500))
    row = scoreboard.top()[0]
    assert row["score"] == scoreboard.MAX_SCORE and row["caught"] == scoreboard.N_BAUBLES
