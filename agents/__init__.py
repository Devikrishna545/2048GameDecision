def make_agent(name: str, jev_budget: float = 3.0):
    if name == "jev":
        from .jev_agent import JevAgent
        return JevAgent(budget_usd=jev_budget)
    if name == "laya":
        from .laya_agent import LayaAgent
        return LayaAgent()
    if name == "laya_lora":
        from .laya_lora import LayaLoraAgent
        return LayaLoraAgent()
    if name == "random":
        from .baselines import RandomAgent
        return RandomAgent()
    if name == "greedy":
        from .baselines import GreedyAgent
        return GreedyAgent()
    raise ValueError(f"unknown agent {name!r}")
