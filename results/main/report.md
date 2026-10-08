# 2048: decision-model comparison

Run `main`. Agents: laya, greedy, random, jev. Every agent played the same seeds, so game k starts from the same board.

## Who is likelier to win

| Agent | Games | Wins (2048) | Win rate (95% CI) | Mean score | Median score | Best score | Mean moves |
|---|---|---|---|---|---|---|---|
| laya | 20 | 0 | 0% (0%–16%) | 1,151 | 1,040 | 2,424 | 124 |
| greedy | 20 | 0 | 0% (0%–16%) | 3,721 | 3,558 | 6,936 | 297 |
| random | 20 | 0 | 0% (0%–16%) | 1,094 | 1,082 | 2,344 | 120 |
| jev | 20 | 0 | 0% (0%–16%) | 3,088 | 2,674 | 7,496 | 251 |

### Largest tile reached

| Agent | 32 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|
| laya | 0 | 10 | 8 | 2 | 0 |
| greedy | 0 | 0 | 4 | 11 | 5 |
| random | 1 | 8 | 10 | 1 | 0 |
| jev | 1 | 1 | 5 | 9 | 4 |

### Head to head on identical seeds

| Pair | First agent higher score | Second agent higher | Tie |
|---|---|---|---|
| laya vs greedy | 1 | 19 | 0 |
| laya vs random | 10 | 10 | 0 |
| laya vs jev | 3 | 17 | 0 |
| greedy vs random | 20 | 0 | 0 |
| greedy vs jev | 14 | 6 | 0 |
| random vs jev | 2 | 18 | 0 |

## How the decisions affect success

Each move is compared with what the options would do. *Agrees with heuristic* means it picked the same move as a simple corner-first rule; *keeps corner* is how often it kept the largest tile in a corner when that was possible; *max-empty* is how often it picked the move leaving the most empty cells.

| Agent | Agrees with heuristic | Keeps corner | Max-empty choice | Mean confidence | Danger: last 10 moves vs earlier | Fallback moves |
|---|---|---|---|---|---|---|
| laya | 48% | 67% | 70% | 0.36 | 0.47 vs 0.50 | 0.0% |
| greedy | 100% | 100% | 100% | n/a | n/a | 0.0% |
| random | 30% | 56% | 73% | n/a | n/a | 0.0% |
| jev | 82% | 100% | 100% | 0.70 | 0.51 vs 0.30 | 0.2% |

**Move mix** (share of moves in each direction):

- laya: up 68%, down 8%, left 10%, right 14%
- greedy: up 54%, down 10%, left 34%, right 1%
- random: up 25%, down 25%, left 24%, right 25%
- jev: up 39%, down 13%, left 41%, right 6%

**Errors** (moves where the model call failed and a fallback move was used):

- jev: RemoteDisconnected ×3, TimeoutError ×4, HTTPError ×6

## Time taken

| Agent | Mean ms / move | p50 | p95 | Mean seconds / game | Total seconds | API cost (USD) |
|---|---|---|---|---|---|---|
| laya | 93.6 | 95.0 | 105.8 | 11.6 | 231.7 | 0.0000 |
| greedy | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0000 |
| random | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0000 |
| jev | 1201.2 | 1153.4 | 1309.0 | 300.3 | 6005.1 | 1.5184 |

## Per-game results

| Agent | Game | Seed | Score | Max tile | Won | Moves | Seconds | Ended by |
|---|---|---|---|---|---|---|---|---|
| laya | 0 | 2048 | 592 | 64 | no | 82 | 8.4 | no_moves |
| laya | 1 | 2049 | 1,360 | 128 | no | 141 | 13.4 | no_moves |
| laya | 2 | 2050 | 724 | 64 | no | 98 | 9.0 | no_moves |
| laya | 3 | 2051 | 1,520 | 128 | no | 157 | 15.3 | no_moves |
| laya | 4 | 2052 | 784 | 64 | no | 102 | 9.7 | no_moves |
| laya | 5 | 2053 | 1,396 | 128 | no | 144 | 13.5 | no_moves |
| laya | 6 | 2054 | 892 | 64 | no | 109 | 10.2 | no_moves |
| laya | 7 | 2055 | 852 | 64 | no | 103 | 9.2 | no_moves |
| laya | 8 | 2056 | 688 | 64 | no | 84 | 7.8 | no_moves |
| laya | 9 | 2057 | 876 | 64 | no | 115 | 10.7 | no_moves |
| laya | 10 | 2058 | 1,188 | 128 | no | 130 | 12.1 | no_moves |
| laya | 11 | 2059 | 2,020 | 256 | no | 162 | 15.3 | no_moves |
| laya | 12 | 2060 | 720 | 64 | no | 97 | 9.0 | no_moves |
| laya | 13 | 2061 | 1,328 | 128 | no | 138 | 12.9 | no_moves |
| laya | 14 | 2062 | 620 | 64 | no | 80 | 7.4 | no_moves |
| laya | 15 | 2063 | 576 | 64 | no | 79 | 7.6 | no_moves |
| laya | 16 | 2064 | 1,612 | 128 | no | 160 | 15.0 | no_moves |
| laya | 17 | 2065 | 1,460 | 128 | no | 150 | 14.1 | no_moves |
| laya | 18 | 2066 | 2,424 | 256 | no | 204 | 18.4 | no_moves |
| laya | 19 | 2067 | 1,380 | 128 | no | 138 | 12.8 | no_moves |
| greedy | 0 | 2048 | 3,556 | 256 | no | 303 | 0.0 | no_moves |
| greedy | 1 | 2049 | 4,296 | 256 | no | 353 | 0.0 | no_moves |
| greedy | 2 | 2050 | 3,072 | 256 | no | 250 | 0.0 | no_moves |
| greedy | 3 | 2051 | 5,952 | 512 | no | 430 | 0.0 | no_moves |
| greedy | 4 | 2052 | 1,720 | 128 | no | 180 | 0.0 | no_moves |
| greedy | 5 | 2053 | 3,436 | 256 | no | 283 | 0.0 | no_moves |
| greedy | 6 | 2054 | 3,560 | 256 | no | 290 | 0.0 | no_moves |
| greedy | 7 | 2055 | 3,532 | 256 | no | 301 | 0.0 | no_moves |
| greedy | 8 | 2056 | 1,920 | 128 | no | 188 | 0.0 | no_moves |
| greedy | 9 | 2057 | 3,592 | 256 | no | 305 | 0.0 | no_moves |
| greedy | 10 | 2058 | 5,060 | 512 | no | 360 | 0.0 | no_moves |
| greedy | 11 | 2059 | 3,996 | 256 | no | 322 | 0.0 | no_moves |
| greedy | 12 | 2060 | 5,620 | 512 | no | 404 | 0.0 | no_moves |
| greedy | 13 | 2061 | 3,628 | 256 | no | 310 | 0.0 | no_moves |
| greedy | 14 | 2062 | 3,440 | 256 | no | 284 | 0.0 | no_moves |
| greedy | 15 | 2063 | 6,936 | 512 | no | 477 | 0.0 | no_moves |
| greedy | 16 | 2064 | 5,396 | 512 | no | 376 | 0.0 | no_moves |
| greedy | 17 | 2065 | 1,868 | 128 | no | 176 | 0.0 | no_moves |
| greedy | 18 | 2066 | 1,376 | 128 | no | 144 | 0.0 | no_moves |
| greedy | 19 | 2067 | 2,464 | 256 | no | 212 | 0.0 | no_moves |
| random | 0 | 2048 | 708 | 64 | no | 88 | 0.0 | no_moves |
| random | 1 | 2049 | 572 | 64 | no | 78 | 0.0 | no_moves |
| random | 2 | 2050 | 1,320 | 128 | no | 137 | 0.0 | no_moves |
| random | 3 | 2051 | 508 | 64 | no | 74 | 0.0 | no_moves |
| random | 4 | 2052 | 1,640 | 128 | no | 167 | 0.0 | no_moves |
| random | 5 | 2053 | 1,264 | 128 | no | 134 | 0.0 | no_moves |
| random | 6 | 2054 | 1,120 | 128 | no | 124 | 0.0 | no_moves |
| random | 7 | 2055 | 1,448 | 128 | no | 150 | 0.0 | no_moves |
| random | 8 | 2056 | 316 | 32 | no | 56 | 0.0 | no_moves |
| random | 9 | 2057 | 984 | 64 | no | 120 | 0.0 | no_moves |
| random | 10 | 2058 | 1,428 | 128 | no | 150 | 0.0 | no_moves |
| random | 11 | 2059 | 1,044 | 128 | no | 112 | 0.0 | no_moves |
| random | 12 | 2060 | 1,428 | 128 | no | 148 | 0.0 | no_moves |
| random | 13 | 2061 | 924 | 64 | no | 113 | 0.0 | no_moves |
| random | 14 | 2062 | 2,344 | 256 | no | 197 | 0.0 | no_moves |
| random | 15 | 2063 | 632 | 64 | no | 87 | 0.0 | no_moves |
| random | 16 | 2064 | 1,416 | 128 | no | 143 | 0.0 | no_moves |
| random | 17 | 2065 | 672 | 64 | no | 87 | 0.0 | no_moves |
| random | 18 | 2066 | 1,296 | 128 | no | 134 | 0.0 | no_moves |
| random | 19 | 2067 | 820 | 64 | no | 102 | 0.0 | no_moves |
| jev | 0 | 2048 | 2,492 | 256 | no | 215 | 313.3 | no_moves |
| jev | 1 | 2049 | 2,652 | 256 | no | 227 | 271.9 | no_moves |
| jev | 2 | 2050 | 1,460 | 128 | no | 154 | 189.9 | no_moves |
| jev | 3 | 2051 | 3,248 | 256 | no | 276 | 357.8 | no_moves |
| jev | 4 | 2052 | 3,336 | 256 | no | 275 | 335.4 | no_moves |
| jev | 5 | 2053 | 7,496 | 512 | no | 525 | 629.9 | no_moves |
| jev | 6 | 2054 | 2,580 | 256 | no | 231 | 270.8 | no_moves |
| jev | 7 | 2055 | 1,792 | 128 | no | 183 | 221.1 | no_moves |
| jev | 8 | 2056 | 5,972 | 512 | no | 417 | 525.3 | no_moves |
| jev | 9 | 2057 | 2,696 | 256 | no | 234 | 274.5 | no_moves |
| jev | 10 | 2058 | 1,388 | 128 | no | 146 | 168.0 | no_moves |
| jev | 11 | 2059 | 1,272 | 128 | no | 128 | 148.2 | no_moves |
| jev | 12 | 2060 | 4,704 | 512 | no | 323 | 370.7 | no_moves |
| jev | 13 | 2061 | 4,848 | 512 | no | 343 | 392.9 | no_moves |
| jev | 14 | 2062 | 564 | 32 | no | 82 | 93.2 | no_moves |
| jev | 15 | 2063 | 3,128 | 256 | no | 261 | 297.8 | no_moves |
| jev | 16 | 2064 | 4,720 | 256 | no | 349 | 402.6 | no_moves |
| jev | 17 | 2065 | 3,820 | 256 | no | 288 | 329.9 | no_moves |
| jev | 18 | 2066 | 2,208 | 128 | no | 207 | 235.7 | no_moves |
| jev | 19 | 2067 | 1,392 | 64 | no | 155 | 176.2 | no_moves |
