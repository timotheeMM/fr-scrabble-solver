"""Finds the highest-scoring legal Scrabble move for a given board and rack."""

from collections import Counter
from dataclasses import dataclass

from .board import SIZE, CENTER, PREMIUMS, letter_multiplier, word_multiplier, is_empty
from .values import get_value, BLANK

BINGO_BONUS = 50
BINGO_TILE_COUNT = 7


@dataclass
class Move:
    word: str
    row: int
    col: int
    direction: str  # "H" or "V"
    score: int
    placements: list  # [(row, col, letter, is_blank), ...] newly placed tiles only


def _segment_ranges(line):
    """(start, end) inclusive ranges whose boundaries don't merge with a
    neighboring tile outside the range."""
    for start in range(SIZE):
        if start > 0 and line[start - 1] is not None:
            continue
        for end in range(start, SIZE):
            if end < SIZE - 1 and line[end + 1] is not None:
                continue
            yield start, end


def _is_connected(line, start, end, empties, orientation, index, board, board_empty):
    if any(line[p] is not None for p in range(start, end + 1)):
        return True
    if board_empty:
        if index == CENTER and start <= CENTER <= end:
            return True
        return False
    for p in empties:
        r, c = (index, p) if orientation == "H" else (p, index)
        if r > 0 and board[r - 1][c] is not None:
            return True
        if r < SIZE - 1 and board[r + 1][c] is not None:
            return True
        if c > 0 and board[r][c - 1] is not None:
            return True
        if c < SIZE - 1 and board[r][c + 1] is not None:
            return True
    return False


def _search_segment(line, start, end, rack_counts, trie):
    """DFS over [start, end] filling empty cells from rack_counts, pruned by
    the dictionary trie. Yields (word, used) where used is a list of
    (pos, letter, is_blank) for newly placed tiles."""
    results = []
    word_chars = [None] * (end - start + 1)
    used = []
    counts = dict(rack_counts)

    def backtrack(pos, node):
        if pos > end:
            if node.is_word:
                results.append(("".join(word_chars), list(used)))
            return
        existing = line[pos]
        if existing is not None:
            letter = existing.lower()
            child = node.children.get(letter)
            if child is None:
                return
            word_chars[pos - start] = letter
            backtrack(pos + 1, child)
            word_chars[pos - start] = None
            return

        for tile, count in list(counts.items()):
            if count <= 0:
                continue
            if tile == BLANK:
                for letter, child in node.children.items():
                    word_chars[pos - start] = letter
                    used.append((pos, letter, True))
                    counts[tile] -= 1
                    backtrack(pos + 1, child)
                    counts[tile] += 1
                    used.pop()
                    word_chars[pos - start] = None
            else:
                child = node.children.get(tile)
                if child is None:
                    continue
                word_chars[pos - start] = tile
                used.append((pos, tile, False))
                counts[tile] -= 1
                backtrack(pos + 1, child)
                counts[tile] += 1
                used.pop()
                word_chars[pos - start] = None

    backtrack(start, trie.root)
    return results


def _score_word(cells_info, positions):
    """cells_info: [(letter, is_blank, is_new), ...] parallel to positions."""
    total = 0
    mult = 1
    for (letter, is_blank, is_new), (r, c) in zip(cells_info, positions):
        value = get_value(letter, is_blank)
        if is_new:
            code = PREMIUMS[r][c]
            value *= letter_multiplier(code)
            mult *= word_multiplier(code)
        total += value
    return total * mult


def _cross_word(board, r, c, new_letter, new_is_blank, orientation):
    """The perpendicular word formed by placing `new_letter` at (r, c), or
    None if the new tile has no perpendicular neighbours."""
    if orientation == "H":
        lo, hi, fixed = r, r, c
        while lo > 0 and board[lo - 1][c] is not None:
            lo -= 1
        while hi < SIZE - 1 and board[hi + 1][c] is not None:
            hi += 1
        if lo == hi:
            return None
        cells_info, positions = [], []
        for i in range(lo, hi + 1):
            positions.append((i, c))
            if i == r:
                cells_info.append((new_letter, new_is_blank, True))
            else:
                cell = board[i][c]
                cells_info.append((cell.lower(), cell.isupper(), False))
    else:
        lo, hi = c, c
        while lo > 0 and board[r][lo - 1] is not None:
            lo -= 1
        while hi < SIZE - 1 and board[r][hi + 1] is not None:
            hi += 1
        if lo == hi:
            return None
        cells_info, positions = [], []
        for j in range(lo, hi + 1):
            positions.append((r, j))
            if j == c:
                cells_info.append((new_letter, new_is_blank, True))
            else:
                cell = board[r][j]
                cells_info.append((cell.lower(), cell.isupper(), False))

    word = "".join(letter for letter, _, _ in cells_info)
    return word, cells_info, positions


def _build_move(board, orientation, index, start, end, word, used, trie):
    line = board[index] if orientation == "H" else [board[r][index] for r in range(SIZE)]

    cells_info, positions = [], []
    for p in range(start, end + 1):
        r, c = (index, p) if orientation == "H" else (p, index)
        positions.append((r, c))
        existing = line[p]
        if existing is not None:
            cells_info.append((existing.lower(), existing.isupper(), False))
        else:
            _, letter, is_blank = next(u for u in used if u[0] == p)
            cells_info.append((letter, is_blank, True))

    score = _score_word(cells_info, positions)

    for pos, letter, is_blank in used:
        r, c = (index, pos) if orientation == "H" else (pos, index)
        cross = _cross_word(board, r, c, letter, is_blank, orientation)
        if cross is None:
            continue
        cross_word, cross_info, cross_positions = cross
        if len(cross_word) > 1 and cross_word not in trie:
            return None
        if len(cross_word) > 1:
            score += _score_word(cross_info, cross_positions)

    if len(used) == BINGO_TILE_COUNT:
        score += BINGO_BONUS

    start_r, start_c = (index, start) if orientation == "H" else (start, index)
    placements = [
        ((index, pos) if orientation == "H" else (pos, index), letter, is_blank)
        for pos, letter, is_blank in used
    ]
    placements = [(r, c, letter, is_blank) for (r, c), letter, is_blank in placements]

    return Move(
        word=word,
        row=start_r,
        col=start_c,
        direction=orientation,
        score=score,
        placements=placements,
    )


def _rack_counts(rack):
    counts = Counter()
    for tile in rack:
        counts[BLANK if tile == BLANK else tile.lower()] += 1
    return counts


def _search_orientation(board, rack_counts, rack_size, trie, orientation):
    board_empty = is_empty(board)
    moves = []
    for index in range(SIZE):
        line = board[index] if orientation == "H" else [board[r][index] for r in range(SIZE)]

        for start, end in _segment_ranges(line):
            empties = [p for p in range(start, end + 1) if line[p] is None]
            if not empties or len(empties) > rack_size:
                continue
            if not _is_connected(line, start, end, empties, orientation, index, board, board_empty):
                continue

            for word, used in _search_segment(line, start, end, rack_counts, trie):
                move = _build_move(board, orientation, index, start, end, word, used, trie)
                if move is not None:
                    moves.append(move)
    return moves


def find_best_moves(board, rack, trie, limit=10):
    counts = _rack_counts(rack)
    rack_size = sum(counts.values())

    moves = _search_orientation(board, counts, rack_size, trie, "H")
    moves += _search_orientation(board, counts, rack_size, trie, "V")

    seen = {}
    for move in moves:
        key = (move.direction, tuple(sorted(move.placements)))
        if key not in seen or move.score > seen[key].score:
            seen[key] = move

    ranked = sorted(seen.values(), key=lambda m: m.score, reverse=True)
    return ranked[:limit]


def best_move(board, rack, trie):
    moves = find_best_moves(board, rack, trie, limit=1)
    return moves[0] if moves else None
