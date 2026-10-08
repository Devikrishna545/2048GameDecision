"""Jev (TypeSafe AI) via its hosted decision API. Needs TYPESAFE_API_KEY (or JEV_API_KEY) in the env or .env.

Every call is paid, so the agent tracks spend from the API's `usage.cost_usd` and
refuses to make calls once `budget_usd` is used up or the account's remaining credit
drops below `reserve_usd`.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from .base import Agent, Decision, parse_system_one


def _load_dotenv(path: Path = Path(__file__).resolve().parent.parent / ".env") -> None:
    """Read KEY=value lines from the project's .env (git-ignored) without overriding the shell."""
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class BudgetExceeded(RuntimeError):
    pass


class JevAgent(Agent):
    name = "jev"

    def __init__(self, timeout: float = 30.0, budget_usd: float = 3.0, reserve_usd: float = 1.0):
        _load_dotenv()
        self.key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("JEV_API_KEY")
        if not self.key:
            raise RuntimeError("TYPESAFE_API_KEY is not set; export it or put it in .env.")
        self.timeout, self.budget_usd, self.reserve_usd = timeout, budget_usd, reserve_usd
        self.spent_usd = 0.0
        self.credits_remaining_usd: float | None = None

    @property
    def out_of_budget(self) -> bool:
        low = self.credits_remaining_usd is not None and self.credits_remaining_usd < self.reserve_usd
        return self.spent_usd >= self.budget_usd or low

    def _decide(self, game, state, questions, legal) -> Decision:
        if self.out_of_budget:
            raise BudgetExceeded(f"spent ${self.spent_usd:.4f} of ${self.budget_usd:.2f} budget")
        body = json.dumps({"state": state, "questions": questions}).encode()
        url = os.environ.get("JEV_API_URL", "https://jevtypesafeai.com/api/v1/decide")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            resp = json.load(r)
        usage = resp.get("usage", {})
        self.spent_usd += usage.get("cost_usd") or 0.0
        if usage.get("credits_remaining_usd") is not None:
            self.credits_remaining_usd = usage["credits_remaining_usd"]
        d = parse_system_one(resp)
        d.cost_usd = usage.get("cost_usd")
        return d
