# 2048: Jev vs Laya

Two "System 1" decision models play 2048 on their own, and every move is logged so we can compare
who is likelier to reach the 2048 tile, how their choices drive the outcome, and how long they take.

| Model | Maker | How it runs |
|---|---|---|
| **Jev** | TypeSafe AI | Hosted API only (`https://api.typesafe.ai/v1/systemone`), needs `TYPESAFE_API_KEY` |
| **Laya** | Convai Innovations | Open weights, Apache 2.0, from Hugging Face [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya), runs locally via `pip install laya` |
| random, greedy | this project | No-model baselines for context |

Both models take the same request: a **state** (board, score, a plain-language description of what
each legal move would do) and two **typed questions**: `move` (a choice among the legal moves) and
`danger` (yes/no probability that the board is about to lock up). Each agent plays the same seeds,
so game *k* starts from the same board for every agent.

## Layout

```
game2048/engine.py     seedable 2048 rules (4x4, 90% 2 / 10% 4 spawns, win = 2048 tile)
agents/base.py         shared request builder, response parser, fallback handling
agents/jev_agent.py    Jev over HTTPS
agents/laya_agent.py   Laya via the local laya Router
agents/baselines.py    random and greedy (corner-first) agents
runner/simulate.py     plays the games, writes logs
runner/report.py       builds report.md from the logs
results/<run_id>/      config.json, games.jsonl, moves_<agent>.jsonl, report.md
tests/test_engine.py   engine checks
```

## Setup

```bash
cd ~/Desktop/2048-jev-vs-laya
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt     # Laya: PyTorch + 843 MB checkpoint on first use
export TYPESAFE_API_KEY=...                    # Jev only
```

## Run

```bash
.venv/bin/python -m runner.simulate --agents laya jev greedy random --games 10 --run-id main
.venv/bin/python -m runner.report results/main
```

Options: `--games`, `--seed-base` (default 2048), `--max-moves` (default 5000), `--quiet`.

## What is logged

`moves_<agent>.jsonl`, one line per move: board before, legal moves, the chosen move, the model's
probability for every option and its confidence, the `danger` probability, what every option would
have done (merges, points, empty cells, corner), the move a simple heuristic would pick, score and
max tile after, latency in ms, whether a fallback was used and why, and the raw model response.

`games.jsonl`, one line per game: score, max tile, won, moves, the move on which 2048 was reached,
wall-clock seconds, model seconds, mean ms per move, fallback count, final board.

If a model call fails or returns an unusable move, the game continues with the model's highest
ranked legal move (or the first legal move on an error), and the move is marked `fallback: true`.
