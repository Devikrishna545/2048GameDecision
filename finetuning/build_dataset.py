"""Build the imitation dataset: Jev and greedy moves on boards 5-19, in the exact format played.

    .venv/bin/python -m finetuning.build_dataset

Boards 0-4 are left out so they can be used as an unseen test. Jev moves that came from a
fallback (the API call failed) are dropped, because they are not Jev's choice.
Each line holds the state and question exactly as `agents.base.build_request` sends them,
plus the index of the teacher's move among the question's options.
"""
from __future__ import annotations

import json
from pathlib import Path

from agents.base import build_request
from game2048.engine import Game2048

ROOT = Path(__file__).resolve().parent.parent
TEACHERS = ("jev", "greedy")
TRAIN_GAMES = range(5, 20)


def game_at(board: list[list[int]], score: int) -> Game2048:
    g = Game2048(seed=0)
    g.board = [row[:] for row in board]
    g.score = score
    return g


def main() -> None:
    out = ROOT / "finetuning" / "data" / "train.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    counts = {}
    with open(out, "w") as f:
        for teacher in TEACHERS:
            n = 0
            for line in open(ROOT / "results" / "main" / f"moves_{teacher}.jsonl"):
                m = json.loads(line)
                if m["game"] not in TRAIN_GAMES or m["fallback"]:
                    continue
                state, questions, legal = build_request(game_at(m["board_before"], m["score_before"]))
                options = list(questions["move"]["criteria"])
                f.write(json.dumps({
                    "teacher": teacher, "game": m["game"], "move_no": m["move_no"],
                    "state": state, "question": questions["move"],
                    "label": options.index(m["move"]),
                }) + "\n")
                n += 1
            counts[teacher] = n
    print(f"wrote {sum(counts.values())} examples to {out}: {counts}")


if __name__ == "__main__":
    main()
