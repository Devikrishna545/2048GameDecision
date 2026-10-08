"""Turn a run's logs into results/<run_id>/report.md.

    python -m runner.report results/<run_id>
"""
from __future__ import annotations

import json
import math
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def pct(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float("nan")


def decision_stats(moves: list[dict]) -> dict:
    n = len(moves) or 1
    corner = [m for m in moves if any(o["max_in_corner"] for o in m["option_outcomes"].values())]
    kept = sum(m["option_outcomes"][m["move"]]["max_in_corner"] for m in corner)
    best_empty = sum(
        m["option_outcomes"][m["move"]]["empty_after"] == max(o["empty_after"] for o in m["option_outcomes"].values())
        for m in moves)
    confs = [m["confidence"] for m in moves if m.get("confidence") is not None]
    # danger calibration: does a high "danger" reading precede the end of the game?
    by_game = defaultdict(list)
    for m in moves:
        by_game[m["game"]].append(m)
    hits = []
    for gm in by_game.values():
        last = gm[-1]["move_no"]
        for m in gm:
            if m.get("danger") is not None:
                hits.append((m["danger"], last - m["move_no"] < 10))
    near_end = [d for d, e in hits if e]
    far = [d for d, e in hits if not e]
    return {
        "moves": len(moves),
        "agree_heuristic": sum(m["move"] == m["heuristic_best"] for m in moves) / n,
        "corner_kept": kept / len(corner) if corner else float("nan"),
        "max_empty_choice": best_empty / n,
        "fallback_rate": sum(m["fallback"] for m in moves) / n,
        "move_mix": Counter(m["move"] for m in moves),
        "mean_conf": st.mean(confs) if confs else None,
        "danger_near_end": st.mean(near_end) if near_end else None,
        "danger_elsewhere": st.mean(far) if far else None,
        "lat": [m["latency_ms"] for m in moves],
        # summed per move: per-game totals are wrong for games run in parallel on one agent
        "cost": sum(m.get("cost_usd") or 0 for m in moves),
        "errors": Counter(m["error"].split(":")[0] for m in moves if m.get("error")),
    }


def main(run_dir: str) -> None:
    run = Path(run_dir)
    games = load_jsonl(run / "games.jsonl")
    agents = list(dict.fromkeys(g["agent"] for g in games))
    G = {a: [g for g in games if g["agent"] == a] for a in agents}
    D = {a: decision_stats(load_jsonl(run / f"moves_{a}.jsonl")) for a in agents}
    L = []
    w = L.append
    w(f"# 2048: decision-model comparison\n\nRun `{run.name}`. Agents: {', '.join(agents)}. "
      f"Every agent played the same seeds, so game k starts from the same board.\n")

    w("## Who is likelier to win\n")
    w("| Agent | Games | Wins (2048) | Win rate (95% CI) | Mean score | Median score | Best score | Mean moves |")
    w("|---|---|---|---|---|---|---|---|")
    for a in agents:
        gs = G[a]
        k = sum(g["won"] for g in gs)
        lo, hi = wilson(k, len(gs))
        sc = [g["score"] for g in gs]
        w(f"| {a} | {len(gs)} | {k} | {k/len(gs):.0%} ({lo:.0%}–{hi:.0%}) | {st.mean(sc):,.0f} | "
          f"{st.median(sc):,.0f} | {max(sc):,} | {st.mean(g['moves'] for g in gs):,.0f} |")
    w("\n### Largest tile reached\n")
    tiles = sorted({g["max_tile"] for g in games})
    w("| Agent | " + " | ".join(str(t) for t in tiles) + " |")
    w("|---|" + "---|" * len(tiles))
    for a in agents:
        c = Counter(g["max_tile"] for g in G[a])
        w(f"| {a} | " + " | ".join(str(c.get(t, 0)) for t in tiles) + " |")

    if len(agents) >= 2:
        w("\n### Head to head on identical seeds\n")
        w("| Pair | First agent higher score | Second agent higher | Tie |")
        w("|---|---|---|---|")
        for i, a in enumerate(agents):
            for b in agents[i + 1:]:
                sa = {g["seed"]: g["score"] for g in G[a]}
                sb = {g["seed"]: g["score"] for g in G[b]}
                common = sa.keys() & sb.keys()
                aw = sum(sa[s] > sb[s] for s in common)
                bw = sum(sb[s] > sa[s] for s in common)
                w(f"| {a} vs {b} | {aw} | {bw} | {len(common) - aw - bw} |")

    w("\n## How the decisions affect success\n")
    w("Each move is compared with what the options would do. *Agrees with heuristic* means it picked the same move "
      "as a simple corner-first rule; *keeps corner* is how often it kept the largest tile in a corner when that "
      "was possible; *max-empty* is how often it picked the move leaving the most empty cells.\n")
    w("| Agent | Agrees with heuristic | Keeps corner | Max-empty choice | Mean confidence | Danger: last 10 moves vs earlier | Fallback moves |")
    w("|---|---|---|---|---|---|---|")
    for a in agents:
        d = D[a]
        conf = f"{d['mean_conf']:.2f}" if d["mean_conf"] is not None else "n/a"
        dang = (f"{d['danger_near_end']:.2f} vs {d['danger_elsewhere']:.2f}"
                if d["danger_near_end"] is not None and d["danger_elsewhere"] is not None else "n/a")
        w(f"| {a} | {d['agree_heuristic']:.0%} | {d['corner_kept']:.0%} | {d['max_empty_choice']:.0%} | "
          f"{conf} | {dang} | {d['fallback_rate']:.1%} |")
    w("\n**Move mix** (share of moves in each direction):\n")
    for a in agents:
        mix = D[a]["move_mix"]
        tot = sum(mix.values()) or 1
        w(f"- {a}: " + ", ".join(f"{m} {mix.get(m, 0)/tot:.0%}" for m in ("up", "down", "left", "right")))
    errs = {a: D[a]["errors"] for a in agents if D[a]["errors"]}
    if errs:
        w("\n**Errors** (moves where the model call failed and a fallback move was used):\n")
        for a, c in errs.items():
            w(f"- {a}: " + ", ".join(f"{k} ×{v}" for k, v in c.items()))

    w("\n## Time taken\n")
    w("| Agent | Mean ms / move | p50 | p95 | Mean seconds / game | Total seconds | API cost (USD) |")
    w("|---|---|---|---|---|---|---|")
    for a in agents:
        lat = D[a]["lat"]
        gs = [g["game_seconds"] for g in G[a]]
        w(f"| {a} | {st.mean(lat):.1f} | {pct(lat, .5):.1f} | {pct(lat, .95):.1f} | {st.mean(gs):.1f} | {sum(gs):.1f} | "
          f"{D[a]['cost']:.4f} |")

    w("\n## Per-game results\n")
    w("| Agent | Game | Seed | Score | Max tile | Won | Moves | Seconds | Ended by |")
    w("|---|---|---|---|---|---|---|---|---|")
    for g in games:
        w(f"| {g['agent']} | {g['game']} | {g['seed']} | {g['score']:,} | {g['max_tile']} | "
          f"{'yes' if g['won'] else 'no'} | {g['moves']} | {g['game_seconds']:.1f} | {g['ended_by']} |")
    (run / "report.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {run / 'report.md'}")


if __name__ == "__main__":
    main(sys.argv[1])
