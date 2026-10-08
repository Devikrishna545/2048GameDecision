"""Laya with the LoRA adapter trained by finetuning/train_lora.py (imitating Jev and greedy)."""
from __future__ import annotations

from pathlib import Path

from .base import Agent, Decision, parse_system_one

ADAPTER = Path(__file__).resolve().parent.parent / "finetuning" / "laya_lora" / "adapter.pt"


class LayaLoraAgent(Agent):
    name = "laya_lora"

    def __init__(self, adapter: Path = ADAPTER):
        import torch

        from finetuning.train_lora import add_lora, load_agent

        if not adapter.exists():
            raise RuntimeError(f"no adapter at {adapter}; run finetuning.train_lora first")
        self.agent = load_agent()
        model = add_lora(self.agent)
        state = torch.load(adapter, map_location="cpu")
        missing = set(state) - {n for n, _ in model.named_parameters()}
        if missing:
            raise RuntimeError(f"adapter has unknown parameters: {sorted(missing)[:3]}")
        model.load_state_dict(state, strict=False)
        model.to(self.agent.device).eval()
        for p in model.parameters():
            p.requires_grad = False

    def _decide(self, game, state, questions, legal) -> Decision:
        return parse_system_one(self.agent.system_one(state, questions))
