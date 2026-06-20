"""15x15 Scrabble board: empty-cell state and premium square layout."""

SIZE = 15
CENTER = SIZE // 2

# Premium square codes: TW/DW = triple/double word, TL/DL = triple/double letter.
_TW = [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)]
_DW = [
    (1, 1), (2, 2), (3, 3), (4, 4), (10, 10), (11, 11), (12, 12), (13, 13),
    (1, 13), (2, 12), (3, 11), (4, 10), (10, 4), (11, 3), (12, 2), (13, 1),
    (CENTER, CENTER),
]
_TL = [
    (1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13),
    (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9),
]
_DL = [
    (0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14),
    (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11),
    (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14),
    (12, 6), (12, 8), (14, 3), (14, 11),
]


def _build_premiums():
    grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    for r, c in _TW:
        grid[r][c] = "TW"
    for r, c in _DW:
        grid[r][c] = "DW"
    for r, c in _TL:
        grid[r][c] = "TL"
    for r, c in _DL:
        grid[r][c] = "DL"
    return grid


PREMIUMS = _build_premiums()


def word_multiplier(code):
    return {"TW": 3, "DW": 2}.get(code, 1)


def letter_multiplier(code):
    return {"TL": 3, "DL": 2}.get(code, 1)


def create_empty_board():
    return [[None for _ in range(SIZE)] for _ in range(SIZE)]


def is_empty(board):
    return all(cell is None for row in board for cell in row)


def transpose(board):
    return [list(row) for row in zip(*board)]
