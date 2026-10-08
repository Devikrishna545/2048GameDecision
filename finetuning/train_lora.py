"""LoRA fine-tune of Laya's encoder to imitate Jev and greedy 2048 moves.

    .venv/bin/python -m finetuning.train_lora --epochs 2
    .venv/bin/python -m finetuning.train_lora --max-steps 20      # timing test only

Laya's own model and tokenisation are used end to end: every example is encoded with
Laya's `_encode_state`, run through its `DecisionModel`, and trained with cross-entropy on
the move question's option logits. LoRA adapters sit on the encoder's attention and MLP
projections (Wqkv, Wo, Wi); the small option scorer is trained in full. Everything else
stays frozen. Game 19 is held out of training as a validation set; boards 0-4 were never
put in the dataset.
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "finetuning" / "data" / "train.jsonl"
OUT = ROOT / "finetuning" / "laya_lora"
VAL_GAMES = {19}


def load_agent(device: str = "mps"):
    import laya
    return laya.load("convaiinnovations/laya", device=device)


def add_lora(agent, rank: int = 16, alpha: int = 32):
    from peft import LoraConfig, inject_adapter_in_model

    model = agent.model
    for p in model.parameters():
        p.requires_grad = False
    cfg = LoraConfig(r=rank, lora_alpha=alpha, lora_dropout=0.05, target_modules=["Wqkv", "Wo", "Wi"])
    inject_adapter_in_model(cfg, model.encoder)
    for n, p in model.named_parameters():
        if "lora_" in n or n.startswith("scorer."):
            p.requires_grad = True
    return model


def trainable_state(model) -> dict:
    return {n: p.detach().cpu() for n, p in model.named_parameters() if p.requires_grad}


def encode(agent, ex: dict):
    from laya.common import collate_items

    internal = {"move": agent._to_internal(ex["question"])}
    items = agent._encode_state(ex["state"], ["move"], internal)
    return items


def batch_tensors(agent, examples: list[dict]):
    from laya.common import collate_items

    groups = [encode(agent, ex) for ex in examples]
    b = collate_items(groups, agent.tok.pad_token_id)
    labels = torch.tensor([ex["label"] for ex in examples], dtype=torch.long)
    return b, labels


def forward(agent, b):
    dev = agent.device
    logits, _ = agent.model(b["input_ids"].to(dev), b["attention_mask"].to(dev),
                            b["marker_pos"].to(dev), b["marker_mask"].to(dev), b["qtype"].to(dev))
    return logits


@torch.no_grad()
def evaluate(agent, examples: list[dict], bs: int = 16) -> float:
    agent.model.eval()
    correct = 0
    for i in range(0, len(examples), bs):
        chunk = examples[i:i + bs]
        b, labels = batch_tensors(agent, chunk)
        correct += (forward(agent, b).argmax(-1).cpu() == labels).sum().item()
    return correct / max(len(examples), 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--max-steps", type=int, default=0, help="stop after this many batches (timing test)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    rows = [json.loads(l) for l in open(DATA)]
    train = [r for r in rows if r["game"] not in VAL_GAMES]
    val = [r for r in rows if r["game"] in VAL_GAMES]
    print(f"train {len(train)}  val {len(val)} (game 19)", flush=True)

    agent = load_agent()
    model = add_lora(agent, rank=args.rank)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"trainable params {n_train / 1e6:.2f}M of {sum(p.numel() for p in model.parameters()) / 1e6:.0f}M",
          flush=True)

    t0 = time.perf_counter()
    base_val = evaluate(agent, val)
    print(f"val accuracy before training: {base_val:.3f} ({time.perf_counter() - t0:.0f}s)", flush=True)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, weight_decay=0.0)
    steps_per_epoch = (len(train) + args.batch - 1) // args.batch
    total = steps_per_epoch * args.epochs // args.accum
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=max(total, 1), pct_start=0.1)

    OUT.mkdir(parents=True, exist_ok=True)
    log = open(OUT / "train_log.jsonl", "a")
    step, t_start = 0, time.perf_counter()
    for epoch in range(args.epochs):
        model.train()
        random.shuffle(train)
        run_loss, run_n = 0.0, 0
        for i in range(0, len(train), args.batch):
            b, labels = batch_tensors(agent, train[i:i + args.batch])
            loss = F.cross_entropy(forward(agent, b), labels.to(agent.device)) / args.accum
            loss.backward()
            step += 1
            run_loss, run_n = run_loss + loss.item() * args.accum, run_n + 1
            if step % args.accum == 0:
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                opt.step()
                opt.zero_grad()
                if sched.last_epoch + 1 < sched.total_steps:
                    sched.step()
            if step % 50 == 0:
                el = time.perf_counter() - t_start
                print(f"epoch {epoch + 1} batch {step}/{steps_per_epoch * args.epochs} loss {run_loss / run_n:.3f} "
                      f"{el / step:.2f}s/batch", flush=True)
                log.write(json.dumps({"epoch": epoch + 1, "batch": step, "loss": run_loss / run_n,
                                      "s_per_batch": el / step}) + "\n")
                log.flush()
                run_loss, run_n = 0.0, 0
            if step % 200 == 0:  # so an interrupted run still leaves a usable adapter
                torch.save(trainable_state(model), OUT / "adapter_partial.pt")
            if args.max_steps and step >= args.max_steps:
                el = time.perf_counter() - t_start
                print(f"timing test: {step} batches in {el:.0f}s = {el / step:.2f}s/batch; "
                      f"one epoch ≈ {el / step * steps_per_epoch / 60:.0f} min", flush=True)
                return
        acc = evaluate(agent, val)
        print(f"epoch {epoch + 1} done, val accuracy {acc:.3f}", flush=True)
        log.write(json.dumps({"epoch": epoch + 1, "val_accuracy": acc}) + "\n")
        log.flush()
        torch.save(trainable_state(model), OUT / "adapter.pt")
    (OUT / "config.json").write_text(json.dumps({**vars(args), "val_before": base_val, "val_after": acc,
                                                 "train_examples": len(train), "val_examples": len(val)}, indent=2))
    print(f"saved {OUT / 'adapter.pt'}", flush=True)


if __name__ == "__main__":
    main()
