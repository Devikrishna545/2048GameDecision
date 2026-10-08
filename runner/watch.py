"""Follow a move log live in readable form.

    .venv/bin/python -m runner.watch results/main/moves_jev.jsonl
"""
from __future__ import annotations

import json
import sys
import time


def fmt(m: dict) -> str:
    probs = " ".join(f"{k}={v:.2f}" for k, v in sorted(m["probabilities"].items(), key=lambda kv: -kv[1]))
    danger = f"{m['danger']:.2f}" if m.get("danger") is not None else "-"
    return (f"game {m['game']:>2} move {m['move_no']:>4}  {m['move']:<5}  score {m['score_after']:>6}  "
            f"max {m['max_tile_after']:>5}  {m['latency_ms']:>7.0f} ms  danger {danger}  [{probs}]"
            + ("  FALLBACK " + str(m.get("error")) if m["fallback"] else ""))


def main(path: str) -> None:
    with open(path) as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            if line.endswith("\n"):
                print(fmt(json.loads(line)), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
