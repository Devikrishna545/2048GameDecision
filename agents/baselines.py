"""Reference agents with no model, so the Jev/Laya numbers have something to be compared against."""
from __future__ import annotations

import random

from .base import Agent, Decision


class RandomAgent(Agent):
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def _decide(self, game, state, questions, legal) -> Decision:
        return Decision(move=self.rng.choice(legal))


def heuristic_value(p: dict) -> float:
    """Simple hand-written rule: corner first, then empty cells, then merges and points."""
    return 1000 * p["max_in_corner"] + 50 * p["empty_after"] + 10 * p["merges"] + p["score_gain"] / 10


class GreedyAgent(Agent):
    name = "greedy"

    def _decide(self, game, state, questions, legal) -> Decision:
        scores = {m: heuristic_value(game.preview(m)) for m in legal}
        return Decision(move=max(scores, key=scores.get))
