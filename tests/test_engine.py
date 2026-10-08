import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from game2048.engine import Game2048, _slide_row_left, apply_move


def test_slide_merges_once_per_tile():
    assert _slide_row_left([2, 2, 2, 2]) == ([4, 4, 0, 0], 8, 2)
    assert _slide_row_left([2, 2, 4, 0]) == ([4, 4, 0, 0], 4, 1)
    assert _slide_row_left([0, 4, 0, 4]) == ([8, 0, 0, 0], 8, 1)


def test_directions():
    b = [[2, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]]
    assert apply_move(b, "right")[0][0] == [0, 0, 0, 4]
    assert apply_move(b, "down")[0][3][0] == 4
    assert apply_move(b, "up")[0][0][0] == 4


def test_seed_is_reproducible():
    a, b = Game2048(seed=7), Game2048(seed=7)
    assert a.board == b.board
    m = a.legal_moves()[0]
    a.step(m), b.step(m)
    assert a.board == b.board


if __name__ == "__main__":
    for f in [test_slide_merges_once_per_tile, test_directions, test_seed_is_reproducible]:
        f()
    print("engine tests passed")
