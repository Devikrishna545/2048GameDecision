# Fine-tuned Laya (LoRA) vs original Laya

**Training.** A LoRA adapter (8.3M trainable parameters, rank 16, on the encoder's Wqkv/Wo/Wi
projections, plus Laya's option scorer) was trained on Laya's own model. The data was 8,111 Jev and
greedy moves from boards 5–18, rebuilt in exact play format. Jev's failed-call moves were dropped.
It ran for 2 epochs on an M5 Pro GPU at about 1.3 s per batch of 8, roughly 45 minutes in total.

**Agreement with the teachers on unseen game 19:** 54.1% before training, 88.5% after epoch 1,
94.3% after epoch 2.

## Held-out boards 0–4 (never in training)

| Player | Mean score | Best tile | Notes |
|---|---|---|---|
| Fine-tuned Laya | 4,182 | 512 (×2) | beat original Laya on 5/5 boards |
| Jev (from `results/main`) | 2,638 | 256 | |
| Greedy rule | 3,719 | 512 | |
| Original Laya | 996 | 128 | |

## 20 fresh boards (seeds 5000–5019, never seen by anyone)

| Player | Mean score | Median | Best tile | ms per move |
|---|---|---|---|---|
| Fine-tuned Laya | 3,747 | 3,220 | 512 (×6) | 114 |
| Original Laya | 1,393 | 1,268 | 256 | 96 |
| Greedy rule | 4,484 | 3,546 | 1024 (×1) | ~0 |
| Random | 1,133 | 1,114 | 256 | ~0 |

Fine-tuned Laya beat original Laya on 19 of 20 fresh boards. Jev was not run on the fresh boards,
because each Jev game costs money.

## What it learned

Fine-tuned Laya now agrees with the greedy corner rule on 98% of moves, against 45% before
training, and keeps the largest tile in a corner whenever it can. In effect it learned that rule
from the move descriptions. It therefore plays close to greedy but slightly below it, and still
never reached 2048. The `danger` question was not trained, so its value for the fine-tuned model
means nothing. Confidence numbers are uncalibrated after fine-tuning.

Full reports: `results/heldout/report.md`, `results/fresh/report.md`. Training log:
`finetuning/laya_lora/train_output.log`.

Reproduce:
    .venv/bin/python -m finetuning.build_dataset
    .venv/bin/python -m finetuning.train_lora --epochs 2
    .venv/bin/python -m runner.simulate --agents laya_lora laya --games 20 --seed-base 5000 --run-id fresh
