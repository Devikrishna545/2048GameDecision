"""Common agent interface plus the shared state/question builder.

Jev and Laya speak the same "System 1" schema (a state plus typed questions),
so both decision models receive byte-identical requests for the same board.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from game2048.engine import Game2048

ARROWS = {"up": "slide up", "down": "slide down", "left": "slide left", "right": "slide right"}


@dataclass
class Decision:
    move: str
    probabilities: dict[str, float] = field(default_factory=dict)
    confidence: float | None = None
    danger: float | None = None          # model's P(board is in danger of filling up)
    raw: dict | None = None              # full model response, for the log
    cost_usd: float | None = None        # paid APIs only
    latency_ms: float = 0.0
    fallback: bool = False               # True when the model's answer could not be used
    error: str | None = None


def describe_option(move: str, p: dict) -> str:
    parts = [ARROWS[move]]
    parts.append(f"merges {p['merges']} pair(s)" if p["merges"] else "no merges")
    parts.append(f"+{p['score_gain']} points")
    parts.append(f"{p['empty_after']} empty cells after")
    parts.append("largest tile stays in a corner" if p["max_in_corner"] else "largest tile leaves the corner")
    return ", ".join(parts)


def build_request(game: Game2048) -> tuple[dict, dict, list[str]]:
    legal = game.legal_moves()
    previews = {m: game.preview(m) for m in legal}
    state = {
        "game": "2048",
        "goal": "Combine equal tiles to reach the 2048 tile. The game is lost when no move is possible.",
        "score": game.score,
        "largest_tile": game.max_tile,
        "empty_cells": sum(v == 0 for row in game.board for v in row),
        "board": game.render(),
        "options": {m: describe_option(m, p) for m, p in previews.items()},
    }
    questions = {
        "move": {
            "type": "choice",
            "instructions": "Which move gives the best chance of eventually reaching the 2048 tile? "
                            "Good 2048 play keeps the largest tile in a corner, keeps cells empty and "
                            "makes merges.",
            "criteria": {m: describe_option(m, p) for m, p in previews.items()},
        },
        "danger": {
            "type": "noul",
            "instructions": "Is the board close to filling up with no merges available (risk of losing)?",
        },
    }
    return state, questions, legal


class Agent:
    name = "agent"

    def decide(self, game: Game2048) -> Decision:
        legal = game.legal_moves()
        state, questions, _ = build_request(game)
        t0 = time.perf_counter()
        try:
            d = self._decide(game, state, questions, legal)
        except Exception as e:
            if type(e).__name__ == "BudgetExceeded":
                raise  # keep the game going, but record what went wrong
            d = Decision(move=legal[0], fallback=True, error=f"{type(e).__name__}: {e}")
        d.latency_ms = (time.perf_counter() - t0) * 1000
        if d.move not in legal:
            ranked = sorted(legal, key=lambda m: d.probabilities.get(m, 0), reverse=True)
            d.error = d.error or f"model chose unusable move {d.move!r}"
            d.move, d.fallback = ranked[0], True
        return d

    def _decide(self, game, state, questions, legal) -> Decision:
        raise NotImplementedError


def parse_system_one(resp: dict) -> Decision:
    """Parse a Jev/Laya style response: answers.move.{choice, probabilities, confidence}."""
    answers = resp.get("answers", {})
    mv = answers.get("move", {})
    probs = mv.get("probabilities") or {}
    if isinstance(probs, list):  # tolerate [{"label":..,"probability":..}] shapes
        probs = {p.get("label") or p.get("choice"): p.get("probability") for p in probs}
    danger = answers.get("danger", {}).get("noul")
    return Decision(
        move=mv.get("choice"),
        probabilities={k: float(v) for k, v in probs.items() if v is not None},
        # top-option probability, so Jev and Laya confidence are measured the same way
        confidence=max(probs.values()) if probs else mv.get("confidence"),
        danger=float(danger) if danger is not None else None,
        raw=resp,
    )
