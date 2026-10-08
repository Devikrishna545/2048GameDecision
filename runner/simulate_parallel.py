"""Play N games of 2048 per agent in parallel (multiple games concurrently).

    python -m runner.simulate_parallel --agents jev --games 10 --jev-budget 2.5 --start-game 12

This is much faster for paid APIs like Jev: 10 games with 4 concurrent players
finishes in 2.5 minutes instead of 50 minutes.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from agents import make_agent
from agents.base import build_request
from game2048.engine import WIN_TILE, Game2048

ROOT = Path(__file__).resolve().parent.parent


def play_sync(agent, seed: int, game_no: int, max_moves: int, move_log, verbose: bool) -> dict:
    """One game, same as serial simulate.py."""
    game = Game2048(seed=seed)
    t_game = time.perf_counter()
    first_win_move = None
    fallbacks = 0
    model_ms = 0.0
    error_streak = 0
    spent_before = getattr(agent, "spent_usd", 0.0)
    ended_by = None
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
        if error_streak >= 5:
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


def heuristic_value(p: dict) -> float:
    return 1000 * p["max_in_corner"] + 50 * p["empty_after"] + 10 * p["merges"] + p["score_gain"] / 10


async def play_game_async(agent, seed: int, game_no: int, max_moves: int, move_log_path: Path, verbose: bool) -> dict:
    """Run one game in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    with open(move_log_path, "a") as move_log:
        return await loop.run_in_executor(None, play_sync, agent, seed, game_no, max_moves, move_log, verbose)


async def main_async(agents: list[str], games: int, seed_base: int, max_moves: int, run_id: str, quiet: bool, start_game: int, jev_budget: float) -> None:
    out = ROOT / "results" / run_id
    out.mkdir(parents=True, exist_ok=True)
    games_log_path = out / "games.jsonl"
    with open(games_log_path, "a") as gl:
        pass
    for name in agents:
        agent = make_agent(name, jev_budget=jev_budget)
        print(f"== {name}: {games} games (parallel, starting from game {start_game})", flush=True)
        move_log_path = out / f"moves_{name}.jsonl"
        tasks = []
        for g in range(start_game, start_game + games):
            task = play_game_async(agent, seed_base + g, g, max_moves, move_log_path, not quiet)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        with open(games_log_path, "a") as gl:
            for res in results:
                gl.write(json.dumps(res) + "\n")
                gl.flush()
    print(f"Logs appended to {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", nargs="+", default=["jev"])
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--start-game", type=int, default=0, help="game number to start from (for resuming)")
    ap.add_argument("--seed-base", type=int, default=2048)
    ap.add_argument("--max-moves", type=int, default=5000)
    ap.add_argument("--run-id", default="main")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--jev-budget", type=float, default=2.5)
    args = ap.parse_args()
    asyncio.run(main_async(args.agents, args.games, args.seed_base, args.max_moves, args.run_id, args.quiet, args.start_game, args.jev_budget))


if __name__ == "__main__":
    main()
