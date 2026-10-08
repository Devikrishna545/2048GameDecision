"""Deterministic, seedable 2048 engine (4x4, 90% 2 / 10% 4 spawns)."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

MOVES = ("up", "down", "left", "right")
WIN_TILE = 2048


def _slide_row_left(row: list[int]) -> tuple[list[int], int, int]:
    """Slide one row left. Returns (new_row, score_gained, merges)."""
    tiles = [v for v in row if v]
    out, gained, merges, i = [], 0, 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            v = tiles[i] * 2
            out.append(v)
            gained += v
            merges += 1
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    out += [0] * (len(row) - len(out))
    return out, gained, merges


def apply_move(board: list[list[int]], move: str) -> tuple[list[list[int]], int, int]:
    """Pure function: board after `move` (no spawn), score gained, merges."""
    n = len(board)
    if move in ("left", "right"):
        rows = [list(r) for r in board]
    else:
        rows = [[board[r][c] for r in range(n)] for c in range(n)]  # columns
    if move in ("right", "down"):
        rows = [r[::-1] for r in rows]
    gained = merges = 0
    new_rows = []
    for r in rows:
        nr, g, m = _slide_row_left(r)
        gained += g
        merges += m
        new_rows.append(nr)
    if move in ("right", "down"):
        new_rows = [r[::-1] for r in new_rows]
    if move in ("up", "down"):
        new_rows = [[new_rows[c][r] for c in range(n)] for r in range(n)]
    return new_rows, gained, merges


def empty_cells(board: list[list[int]]) -> list[tuple[int, int]]:
    return [(r, c) for r, row in enumerate(board) for c, v in enumerate(row) if v == 0]


def max_tile(board: list[list[int]]) -> int:
    return max(max(row) for row in board)


@dataclass
class Game2048:
    seed: int | None = None
    size: int = 4
    board: list[list[int]] = field(init=False)
    score: int = field(default=0, init=False)
    moves_made: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.board = [[0] * self.size for _ in range(self.size)]
        self._spawn()
        self._spawn()

    def _spawn(self) -> None:
        cells = empty_cells(self.board)
        if cells:
            r, c = self.rng.choice(cells)
            self.board[r][c] = 4 if self.rng.random() < 0.1 else 2

    def legal_moves(self) -> list[str]:
        return [m for m in MOVES if apply_move(self.board, m)[0] != self.board]

    def preview(self, move: str) -> dict:
        """What a move would do, without spawning. Used to describe options to agents."""
        nb, gained, merges = apply_move(self.board, move)
        return {
            "board": nb,
            "score_gain": gained,
            "merges": merges,
            "empty_after": len(empty_cells(nb)),
            "max_tile_after": max_tile(nb),
            "max_in_corner": max_tile(nb) in (nb[0][0], nb[0][-1], nb[-1][0], nb[-1][-1]),
        }

    def step(self, move: str) -> int:
        nb, gained, _ = apply_move(self.board, move)
        if nb == self.board:
            raise ValueError(f"illegal move: {move}")
        self.board = nb
        self.score += gained
        self.moves_made += 1
        self._spawn()
        return gained

    @property
    def max_tile(self) -> int:
        return max_tile(self.board)

    @property
    def won(self) -> bool:
        return self.max_tile >= WIN_TILE

    @property
    def over(self) -> bool:
        return not self.legal_moves()

    def render(self) -> str:
        return "\n".join(" ".join(f"{v or '.':>5}" for v in row) for row in self.board)
