"""Laya (Convai Innovations), open weights from Hugging Face, run locally via the `laya` package."""
from __future__ import annotations

from .base import Agent, Decision, parse_system_one


class LayaAgent(Agent):
    name = "laya"

    def __init__(self, checkpoint: str = "english"):
        from laya import Router  # imported lazily so other agents run without torch

        self.checkpoint = checkpoint
        self.router = Router()
        self.router.predict("warm-up", {"ok": {"type": "noul", "instructions": "Is this a test?"}},
                            model=checkpoint)

    def _decide(self, game, state, questions, legal) -> Decision:
        return parse_system_one(self.router.predict(state, questions, model=self.checkpoint))
