"""Letter point values for French Scrabble. Blank tiles are worth 0."""

LETTER_VALUES = {
    "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4, "g": 2, "h": 4,
    "i": 1, "j": 8, "k": 10, "l": 1, "m": 2, "n": 1, "o": 1, "p": 3,
    "q": 8, "r": 1, "s": 1, "t": 1, "u": 1, "v": 4, "w": 10, "x": 10,
    "y": 10, "z": 10,
}

BLANK = "?"


def get_value(letter: str, is_blank: bool = False) -> int:
    if is_blank or letter == BLANK:
        return 0
    return LETTER_VALUES.get(letter.lower(), 0)
