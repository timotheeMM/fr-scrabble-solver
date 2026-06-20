"""Loads the French word list into a trie for fast prefix-pruned search."""

from pathlib import Path

DEFAULT_WORDS_PATH = Path(__file__).resolve().parent.parent.parent / "words.txt"


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for letter in word:
            node = node.children.setdefault(letter, TrieNode())
        node.is_word = True

    def __contains__(self, word: str) -> bool:
        node = self.root
        for letter in word:
            node = node.children.get(letter)
            if node is None:
                return False
        return node.is_word


def load_dictionary(path: Path = DEFAULT_WORDS_PATH) -> Trie:
    trie = Trie()
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                trie.insert(word)
    return trie
