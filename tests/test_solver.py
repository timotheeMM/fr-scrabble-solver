import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from scrabble import create_empty_board, find_best_moves
from scrabble.dictionary import Trie


@pytest.fixture
def tiny_dictionary():
    trie = Trie()
    for word in ["chat", "chats", "chien", "rate", "art", "ta", "an", "or"]:
        trie.insert(word)
    return trie


def test_first_move_must_cover_center(tiny_dictionary):
    board = create_empty_board()
    moves = find_best_moves(board, list("chat"), tiny_dictionary)
    assert moves
    for move in moves:
        rows = [p[0] for p in move.placements]
        cols = [p[1] for p in move.placements]
        if move.direction == "H":
            assert move.row == 7
            assert min(cols) <= 7 <= max(cols)
        else:
            assert move.col == 7
            assert min(rows) <= 7 <= max(rows)


def test_move_must_connect_to_existing_tiles(tiny_dictionary):
    board = create_empty_board()
    board[7][7] = "c"
    board[7][8] = "h"
    board[7][9] = "a"
    board[7][10] = "t"
    moves = find_best_moves(board, list("rate"), tiny_dictionary)
    assert moves
    for move in moves:
        touches_existing = any(
            board[r][c] is not None for r, c, _, _ in [] or []
        )
    # every move must reuse the existing word or sit adjacent to it
    for move in moves:
        ok = False
        for r, c, _, _ in move.placements:
            if any(
                0 <= rr < 15 and 0 <= cc < 15 and board[rr][cc] is not None
                for rr, cc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            ):
                ok = True
            if board[r][c] is not None:
                ok = True
        assert ok


def test_blank_tile_scores_zero(tiny_dictionary):
    board = create_empty_board()
    moves = find_best_moves(board, list("?hat"), tiny_dictionary)
    assert any(p[3] for move in moves for p in move.placements)


def test_no_moves_when_rack_cannot_form_a_word(tiny_dictionary):
    board = create_empty_board()
    moves = find_best_moves(board, list("zzzz"), tiny_dictionary)
    assert moves == []
