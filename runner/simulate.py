"""Play N games of 2048 per agent and log every move.

    python -m runner.simulate --agents laya jev --games 10

Each agent plays the same seeds, so game k starts from the same board for everyone.
Output goes to results/<run_id>/: moves_<agent>.jsonl (one line per move) and games.jsonl.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from agents import make_agent
from agents.baselines import heuristic_value
from game2048.engine import WIN_TILE, Game2048

ROOT = Path(__file__).resolve().parent.parent


def play(agent, seed: int, game_no: int, max_moves: int, move_log, verbose: bool) -> dict:
    game = Game2048(seed=seed)
    spent_before = getattr(agent, "spent_usd", 0.0)
    t_game = time.perf_counter()
    first_win_move = None
    fallbacks = 0
    model_ms = 0.0
    ended_by = None
    error_streak = 0
    while not game.over and game.moves_made < max_moves:
        if getattr(agent, "out_of_budget", False):
            ended_by = "budget"
            break
        legal = game.legal_moves()
        previews = {m: game.preview(m) for m in legal}
        board_before, score_before = [r[:] for r in game.board], game.score
        try:
            d = agent.decide(game)
        except RuntimeError as e:
            if type(e).__name__ != "BudgetExceeded":
                raise
            ended_by = "budget"
            break
        error_streak = error_streak + 1 if d.error and d.raw is None else 0
        if error_streak >= 5:  # API down or out of credit: stop instead of logging junk moves
            ended_by = "errors"
            print(f"  [{agent.name}] 5 failed calls in a row, last: {d.error}", flush=True)
            break
        heur = {m: heuristic_value(p) for m, p in previews.items()}
        gained = game.step(d.move)
        fallbacks += d.fallback
        model_ms += d.latency_ms
        if game.won and first_win_move is None:
            first_win_move = game.moves_made
        move_log.write(json.dumps({
            "agent": agent.name, "game": game_no, "seed": seed, "move_no": game.moves_made,
            "board_before": board_before, "score_before": score_before, "legal_moves": legal,
            "move": d.move, "probabilities": d.probabilities, "confidence": d.confidence,
            "danger": d.danger, "fallback": d.fallback, "error": d.error,
            "option_outcomes": {m: {k: v for k, v in p.items() if k != "board"} for m, p in previews.items()},
            "heuristic_best": max(heur, key=heur.get),
            "score_gain": gained, "score_after": game.score, "max_tile_after": game.max_tile,
            "empty_after": sum(v == 0 for r in game.board for v in r),
            "latency_ms": round(d.latency_ms, 3), "cost_usd": d.cost_usd, "raw_response": d.raw,
        }) + "\n")
    elapsed = time.perf_counter() - t_game
    result = {
        "agent": agent.name, "game": game_no, "seed": seed, "score": game.score,
        "max_tile": game.max_tile, "won": game.won, "moves": game.moves_made,
        "win_at_move": first_win_move, "ended_by": ended_by or ("no_moves" if game.over else "move_cap"),
        "game_seconds": round(elapsed, 3), "model_seconds": round(model_ms / 1000, 3),
        "mean_ms_per_move": round(model_ms / max(game.moves_made, 1), 3), "fallback_moves": fallbacks,
        "cost_usd": round(getattr(agent, "spent_usd", 0.0) - spent_before, 6),
        "final_board": game.board,
    }
    if verbose:
        print(f"  [{agent.name}] game {game_no} seed {seed}: score {game.score}, max {game.max_tile}, "
              f"{'WON' if game.won else 'lost'}, {game.moves_made} moves, {elapsed:.1f}s"
              + (f", ${result['cost_usd']:.4f}" if result["cost_usd"] else "")
              + (" [stopped: budget]" if result["ended_by"] == "budget" else ""), flush=True)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", nargs="+", default=["laya", "jev"])
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--seed-base", type=int, default=2048)
    ap.add_argument("--max-moves", type=int, default=5000)
    ap.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--jev-budget", type=float, default=3.0, help="max USD to spend on Jev calls this run")
    args = ap.parse_args()

    out = ROOT / "results" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps({**vars(args), "win_tile": WIN_TILE}, indent=2))
    with open(out / "games.jsonl", "a") as games_log:
        for name in args.agents:
            agent = make_agent(name, jev_budget=args.jev_budget)
            print(f"== {name}: {args.games} games", flush=True)
            with open(out / f"moves_{name}.jsonl", "a") as move_log:
                for g in range(args.games):
                    if getattr(agent, "out_of_budget", False):
                        print(f"  [{name}] budget reached (${agent.spent_usd:.2f} spent); stopping.", flush=True)
                        break
                    res = play(agent, args.seed_base + g, g, args.max_moves, move_log, not args.quiet)
                    games_log.write(json.dumps(res) + "\n")
                    if res["ended_by"] == "errors":
                        print(f"  [{name}] stopping after repeated errors.", flush=True)
                        break
                    games_log.flush()
    print(f"Logs written to {out}")


if __name__ == "__main__":
    main()
