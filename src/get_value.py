from values import values


def get_value(word):
    value = 0
    for char in word:
        value += values.get(char, None)
    return value
