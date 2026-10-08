# 2048: decision-model comparison

Run `fresh`. Agents: laya_lora, laya, greedy, random. Every agent played the same seeds, so game k starts from the same board.

## Who is likelier to win

| Agent | Games | Wins (2048) | Win rate (95% CI) | Mean score | Median score | Best score | Mean moves |
|---|---|---|---|---|---|---|---|
| laya_lora | 20 | 0 | 0% (0%–16%) | 3,747 | 3,220 | 7,824 | 295 |
| laya | 20 | 0 | 0% (0%–16%) | 1,393 | 1,268 | 2,772 | 143 |
| greedy | 20 | 0 | 0% (0%–16%) | 4,484 | 3,546 | 12,436 | 338 |
| random | 20 | 0 | 0% (0%–16%) | 1,133 | 1,114 | 2,612 | 122 |

### Largest tile reached

| Agent | 32 | 64 | 128 | 256 | 512 | 1024 |
|---|---|---|---|---|---|---|
| laya_lora | 0 | 1 | 4 | 9 | 6 | 0 |
| laya | 0 | 9 | 7 | 4 | 0 | 0 |
| greedy | 0 | 1 | 1 | 12 | 5 | 1 |
| random | 2 | 6 | 10 | 2 | 0 | 0 |

### Head to head on identical seeds

| Pair | First agent higher score | Second agent higher | Tie |
|---|---|---|---|
| laya_lora vs laya | 19 | 1 | 0 |
| laya_lora vs greedy | 6 | 12 | 2 |
| laya_lora vs random | 17 | 3 | 0 |
| laya vs greedy | 1 | 19 | 0 |
| laya vs random | 13 | 7 | 0 |
| greedy vs random | 18 | 2 | 0 |

## How the decisions affect success

Each move is compared with what the options would do. *Agrees with heuristic* means it picked the same move as a simple corner-first rule; *keeps corner* is how often it kept the largest tile in a corner when that was possible; *max-empty* is how often it picked the move leaving the most empty cells.

| Agent | Agrees with heuristic | Keeps corner | Max-empty choice | Mean confidence | Danger: last 10 moves vs earlier | Fallback moves |
|---|---|---|---|---|---|---|
| laya_lora | 98% | 100% | 100% | 0.90 | 0.79 vs 0.73 | 0.0% |
| laya | 45% | 72% | 68% | 0.36 | 0.46 vs 0.50 | 0.0% |
| greedy | 100% | 100% | 100% | n/a | n/a | 0.0% |
| random | 31% | 56% | 74% | n/a | n/a | 0.0% |

**Move mix** (share of moves in each direction):

- laya_lora: up 53%, down 12%, left 35%, right 1%
- laya: up 69%, down 7%, left 9%, right 15%
- greedy: up 56%, down 10%, left 34%, right 1%
- random: up 25%, down 25%, left 25%, right 25%

## Time taken

| Agent | Mean ms / move | p50 | p95 | Mean seconds / game | Total seconds | API cost (USD) |
|---|---|---|---|---|---|---|
| laya_lora | 113.5 | 115.4 | 125.4 | 33.6 | 671.4 | 0.0000 |
| laya | 95.7 | 97.1 | 109.5 | 13.7 | 273.9 | 0.0000 |
| greedy | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0000 |
| random | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0000 |

## Per-game results

| Agent | Game | Seed | Score | Max tile | Won | Moves | Seconds | Ended by |
|---|---|---|---|---|---|---|---|---|
| laya_lora | 0 | 5000 | 7,824 | 512 | no | 543 | 60.8 | no_moves |
| laya_lora | 1 | 5001 | 5,764 | 512 | no | 412 | 46.0 | no_moves |
| laya_lora | 2 | 5002 | 4,232 | 256 | no | 345 | 38.3 | no_moves |
| laya_lora | 3 | 5003 | 3,092 | 256 | no | 265 | 29.9 | no_moves |
| laya_lora | 4 | 5004 | 1,508 | 128 | no | 161 | 17.4 | no_moves |
| laya_lora | 5 | 5005 | 3,120 | 256 | no | 260 | 29.0 | no_moves |
| laya_lora | 6 | 5006 | 3,416 | 256 | no | 285 | 32.0 | no_moves |
| laya_lora | 7 | 5007 | 1,832 | 128 | no | 186 | 20.4 | no_moves |
| laya_lora | 8 | 5008 | 1,396 | 128 | no | 145 | 16.1 | no_moves |
| laya_lora | 9 | 5009 | 1,460 | 64 | no | 167 | 19.1 | no_moves |
| laya_lora | 10 | 5010 | 3,288 | 256 | no | 280 | 31.3 | no_moves |
| laya_lora | 11 | 5011 | 5,328 | 512 | no | 369 | 41.5 | no_moves |
| laya_lora | 12 | 5012 | 3,152 | 256 | no | 263 | 29.2 | no_moves |
| laya_lora | 13 | 5013 | 5,628 | 512 | no | 396 | 49.4 | no_moves |
| laya_lora | 14 | 5014 | 3,356 | 256 | no | 274 | 37.5 | no_moves |
| laya_lora | 15 | 5015 | 2,264 | 256 | no | 186 | 21.4 | no_moves |
| laya_lora | 16 | 5016 | 6,856 | 512 | no | 476 | 53.6 | no_moves |
| laya_lora | 17 | 5017 | 7,176 | 512 | no | 504 | 55.6 | no_moves |
| laya_lora | 18 | 5018 | 1,784 | 128 | no | 181 | 20.1 | no_moves |
| laya_lora | 19 | 5019 | 2,472 | 256 | no | 210 | 22.8 | no_moves |
| laya | 0 | 5000 | 736 | 64 | no | 97 | 9.0 | no_moves |
| laya | 1 | 5001 | 624 | 64 | no | 87 | 8.3 | no_moves |
| laya | 2 | 5002 | 2,040 | 128 | no | 189 | 17.9 | no_moves |
| laya | 3 | 5003 | 1,472 | 128 | no | 153 | 15.1 | no_moves |
| laya | 4 | 5004 | 924 | 64 | no | 113 | 10.6 | no_moves |
| laya | 5 | 5005 | 976 | 64 | no | 114 | 10.6 | no_moves |
| laya | 6 | 5006 | 1,484 | 128 | no | 154 | 14.3 | no_moves |
| laya | 7 | 5007 | 1,292 | 128 | no | 133 | 12.7 | no_moves |
| laya | 8 | 5008 | 1,244 | 128 | no | 136 | 12.6 | no_moves |
| laya | 9 | 5009 | 976 | 64 | no | 118 | 11.3 | no_moves |
| laya | 10 | 5010 | 724 | 64 | no | 95 | 8.9 | no_moves |
| laya | 11 | 5011 | 888 | 64 | no | 107 | 10.1 | no_moves |
| laya | 12 | 5012 | 988 | 64 | no | 125 | 12.6 | no_moves |
| laya | 13 | 5013 | 1,616 | 128 | no | 172 | 16.6 | no_moves |
| laya | 14 | 5014 | 820 | 64 | no | 106 | 10.4 | no_moves |
| laya | 15 | 5015 | 2,196 | 256 | no | 179 | 16.9 | no_moves |
| laya | 16 | 5016 | 2,424 | 256 | no | 205 | 19.3 | no_moves |
| laya | 17 | 5017 | 2,772 | 256 | no | 242 | 23.8 | no_moves |
| laya | 18 | 5018 | 2,364 | 256 | no | 200 | 19.6 | no_moves |
| laya | 19 | 5019 | 1,300 | 128 | no | 134 | 13.2 | no_moves |
| greedy | 0 | 5000 | 8,416 | 512 | no | 579 | 0.0 | no_moves |
| greedy | 1 | 5001 | 3,552 | 256 | no | 299 | 0.0 | no_moves |
| greedy | 2 | 5002 | 5,620 | 512 | no | 388 | 0.0 | no_moves |
| greedy | 3 | 5003 | 5,776 | 512 | no | 410 | 0.0 | no_moves |
| greedy | 4 | 5004 | 2,772 | 256 | no | 227 | 0.0 | no_moves |
| greedy | 5 | 5005 | 3,500 | 256 | no | 294 | 0.0 | no_moves |
| greedy | 6 | 5006 | 3,416 | 256 | no | 285 | 0.0 | no_moves |
| greedy | 7 | 5007 | 7,720 | 512 | no | 532 | 0.0 | no_moves |
| greedy | 8 | 5008 | 4,116 | 256 | no | 337 | 0.0 | no_moves |
| greedy | 9 | 5009 | 1,920 | 128 | no | 198 | 0.0 | no_moves |
| greedy | 10 | 5010 | 6,536 | 512 | no | 442 | 0.0 | no_moves |
| greedy | 11 | 5011 | 4,228 | 256 | no | 348 | 0.0 | no_moves |
| greedy | 12 | 5012 | 3,152 | 256 | no | 263 | 0.0 | no_moves |
| greedy | 13 | 5013 | 3,540 | 256 | no | 286 | 0.0 | no_moves |
| greedy | 14 | 5014 | 2,840 | 256 | no | 242 | 0.0 | no_moves |
| greedy | 15 | 5015 | 2,484 | 256 | no | 212 | 0.0 | no_moves |
| greedy | 16 | 5016 | 3,596 | 256 | no | 301 | 0.0 | no_moves |
| greedy | 17 | 5017 | 12,436 | 1024 | no | 753 | 0.1 | no_moves |
| greedy | 18 | 5018 | 3,180 | 256 | no | 263 | 0.0 | no_moves |
| greedy | 19 | 5019 | 876 | 64 | no | 111 | 0.0 | no_moves |
| random | 0 | 5000 | 1,136 | 128 | no | 122 | 0.0 | no_moves |
| random | 1 | 5001 | 1,092 | 128 | no | 121 | 0.0 | no_moves |
| random | 2 | 5002 | 576 | 64 | no | 79 | 0.0 | no_moves |
| random | 3 | 5003 | 744 | 64 | no | 99 | 0.0 | no_moves |
| random | 4 | 5004 | 1,668 | 128 | no | 170 | 0.0 | no_moves |
| random | 5 | 5005 | 708 | 64 | no | 95 | 0.0 | no_moves |
| random | 6 | 5006 | 1,188 | 128 | no | 129 | 0.0 | no_moves |
| random | 7 | 5007 | 644 | 64 | no | 88 | 0.0 | no_moves |
| random | 8 | 5008 | 1,612 | 128 | no | 162 | 0.0 | no_moves |
| random | 9 | 5009 | 668 | 64 | no | 92 | 0.0 | no_moves |
| random | 10 | 5010 | 664 | 64 | no | 91 | 0.0 | no_moves |
| random | 11 | 5011 | 284 | 32 | no | 54 | 0.0 | no_moves |
| random | 12 | 5012 | 1,380 | 128 | no | 143 | 0.0 | no_moves |
| random | 13 | 5013 | 1,436 | 128 | no | 148 | 0.0 | no_moves |
| random | 14 | 5014 | 1,256 | 128 | no | 131 | 0.0 | no_moves |
| random | 15 | 5015 | 2,612 | 256 | no | 219 | 0.0 | no_moves |
| random | 16 | 5016 | 2,296 | 256 | no | 198 | 0.0 | no_moves |
| random | 17 | 5017 | 328 | 32 | no | 60 | 0.0 | no_moves |
| random | 18 | 5018 | 1,336 | 128 | no | 137 | 0.0 | no_moves |
| random | 19 | 5019 | 1,024 | 128 | no | 109 | 0.0 | no_moves |
