# 2048: decision-model comparison

Run `heldout`. Agents: laya_lora, laya, greedy, random. Every agent played the same seeds, so game k starts from the same board.

## Who is likelier to win

| Agent | Games | Wins (2048) | Win rate (95% CI) | Mean score | Median score | Best score | Mean moves |
|---|---|---|---|---|---|---|---|
| laya_lora | 5 | 0 | 0% (0%–43%) | 4,182 | 3,556 | 6,780 | 322 |
| laya | 5 | 0 | 0% (0%–43%) | 996 | 784 | 1,520 | 116 |
| greedy | 5 | 0 | 0% (0%–43%) | 3,719 | 3,556 | 5,952 | 303 |
| random | 5 | 0 | 0% (0%–43%) | 950 | 708 | 1,640 | 109 |

### Largest tile reached

| Agent | 64 | 128 | 256 | 512 |
|---|---|---|---|---|
| laya_lora | 0 | 1 | 2 | 2 |
| laya | 3 | 2 | 0 | 0 |
| greedy | 0 | 1 | 3 | 1 |
| random | 3 | 2 | 0 | 0 |

### Head to head on identical seeds

| Pair | First agent higher score | Second agent higher | Tie |
|---|---|---|---|
| laya_lora vs laya | 5 | 0 | 0 |
| laya_lora vs greedy | 3 | 1 | 1 |
| laya_lora vs random | 5 | 0 | 0 |
| laya vs greedy | 0 | 5 | 0 |
| laya vs random | 2 | 3 | 0 |
| greedy vs random | 5 | 0 | 0 |

## How the decisions affect success

Each move is compared with what the options would do. *Agrees with heuristic* means it picked the same move as a simple corner-first rule; *keeps corner* is how often it kept the largest tile in a corner when that was possible; *max-empty* is how often it picked the move leaving the most empty cells.

| Agent | Agrees with heuristic | Keeps corner | Max-empty choice | Mean confidence | Danger: last 10 moves vs earlier | Fallback moves |
|---|---|---|---|---|---|---|
| laya_lora | 96% | 100% | 100% | 0.92 | 0.77 vs 0.75 | 0.0% |
| laya | 47% | 70% | 67% | 0.36 | 0.47 vs 0.51 | 0.0% |
| greedy | 100% | 100% | 100% | n/a | n/a | 0.0% |
| random | 30% | 53% | 73% | n/a | n/a | 0.0% |

**Move mix** (share of moves in each direction):

- laya_lora: up 49%, down 16%, left 34%, right 2%
- laya: up 71%, down 7%, left 9%, right 12%
- greedy: up 54%, down 11%, left 33%, right 1%
- random: up 27%, down 23%, left 24%, right 26%

## Time taken

| Agent | Mean ms / move | p50 | p95 | Mean seconds / game | Total seconds | API cost (USD) |
|---|---|---|---|---|---|---|
| laya_lora | 111.2 | 114.6 | 126.4 | 35.9 | 179.3 | 0.0000 |
| laya | 95.8 | 98.2 | 105.8 | 11.1 | 55.6 | 0.0000 |
| greedy | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0000 |
| random | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0000 |

## Per-game results

| Agent | Game | Seed | Score | Max tile | Won | Moves | Seconds | Ended by |
|---|---|---|---|---|---|---|---|---|
| laya_lora | 0 | 2048 | 3,556 | 256 | no | 303 | 34.8 | no_moves |
| laya_lora | 1 | 2049 | 5,752 | 512 | no | 412 | 45.4 | no_moves |
| laya_lora | 2 | 2050 | 2,888 | 256 | no | 238 | 26.0 | no_moves |
| laya_lora | 3 | 2051 | 6,780 | 512 | no | 470 | 52.1 | no_moves |
| laya_lora | 4 | 2052 | 1,936 | 128 | no | 188 | 21.0 | no_moves |
| laya | 0 | 2048 | 592 | 64 | no | 82 | 8.0 | no_moves |
| laya | 1 | 2049 | 1,360 | 128 | no | 141 | 13.4 | no_moves |
| laya | 2 | 2050 | 724 | 64 | no | 98 | 9.3 | no_moves |
| laya | 3 | 2051 | 1,520 | 128 | no | 157 | 15.1 | no_moves |
| laya | 4 | 2052 | 784 | 64 | no | 102 | 9.8 | no_moves |
| greedy | 0 | 2048 | 3,556 | 256 | no | 303 | 0.0 | no_moves |
| greedy | 1 | 2049 | 4,296 | 256 | no | 353 | 0.0 | no_moves |
| greedy | 2 | 2050 | 3,072 | 256 | no | 250 | 0.0 | no_moves |
| greedy | 3 | 2051 | 5,952 | 512 | no | 430 | 0.0 | no_moves |
| greedy | 4 | 2052 | 1,720 | 128 | no | 180 | 0.0 | no_moves |
| random | 0 | 2048 | 708 | 64 | no | 88 | 0.0 | no_moves |
| random | 1 | 2049 | 572 | 64 | no | 78 | 0.0 | no_moves |
| random | 2 | 2050 | 1,320 | 128 | no | 137 | 0.0 | no_moves |
| random | 3 | 2051 | 508 | 64 | no | 74 | 0.0 | no_moves |
| random | 4 | 2052 | 1,640 | 128 | no | 167 | 0.0 | no_moves |
