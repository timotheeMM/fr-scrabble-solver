"""Flask web GUI for the French Scrabble solver."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from flask import Flask, jsonify, render_template, request

from scrabble import PREMIUMS, SIZE, find_best_moves, load_dictionary

app = Flask(__name__)
DICTIONARY = load_dictionary()

VALID_LETTERS = set("abcdefghijklmnopqrstuvwxyz")


def _parse_board(raw):
    board = [[None] * SIZE for _ in range(SIZE)]
    for r in range(min(SIZE, len(raw or []))):
        row = raw[r] or []
        for c in range(min(SIZE, len(row))):
            cell = row[c]
            if cell and cell.lower() in VALID_LETTERS:
                board[r][c] = cell
    return board


def _parse_rack(raw):
    rack = []
    for tile in raw or "":
        if tile == "?":
            rack.append("?")
        elif tile.lower() in VALID_LETTERS:
            rack.append(tile.lower())
    return rack


@app.route("/")
def index():
    return render_template("index.html", size=SIZE, premiums=PREMIUMS, center=SIZE // 2)


@app.route("/api/best-moves", methods=["POST"])
def api_best_moves():
    data = request.get_json(force=True, silent=True) or {}
    board = _parse_board(data.get("board"))
    rack = _parse_rack(data.get("rack"))

    if not rack:
        return jsonify({"error": "Indique au moins une lettre dans ton jeu."}), 400
    if len(rack) > 7:
        return jsonify({"error": "Un jeu Scrabble contient au maximum 7 lettres."}), 400

    moves = find_best_moves(board, rack, DICTIONARY, limit=5)
    if not moves:
        return jsonify({"moves": []})

    return jsonify(
        {
            "moves": [
                {
                    "word": m.word,
                    "score": m.score,
                    "row": m.row,
                    "col": m.col,
                    "direction": m.direction,
                    "placements": [
                        {"row": r, "col": c, "letter": letter, "blank": is_blank}
                        for r, c, letter, is_blank in m.placements
                    ],
                }
                for m in moves
            ]
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
