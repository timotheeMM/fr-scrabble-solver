# fr-scrabble-solver

Solveur de Scrabble en français : donne le meilleur coup possible à partir de l'état du plateau et des lettres en main.

## Fonctionnalités

- Plateau 15x15 avec toutes les cases bonus officielles (mots/lettres comptes double et triple).
- Dictionnaire français de 300 000+ mots, recherche par trie pour un calcul rapide.
- Gestion des lettres blanches (jokers), des mots croisés, et du bonus de 50 points pour un "scrabble" (7 lettres posées).
- Interface web pour placer les pions du plateau, entrer son jeu, et visualiser le meilleur coup (et 4 alternatives) directement sur le plateau.

## Installation

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'interface graphique

```sh
python app.py
```

Puis ouvrir [http://127.0.0.1:5050](http://127.0.0.1:5050).

- Tape une lettre dans le champ "Poser un pion", coche "Lettre blanche" si besoin, puis clique une case du plateau pour la poser. Re-clique une case occupée pour l'effacer.
- Entre tes lettres dans "Ton jeu" (utilise `?` pour un joker), puis clique "Trouver le meilleur coup".
- Clique un coup dans la liste pour le visualiser sur le plateau, ou "Appliquer ce coup" pour le poser.

## Structure du projet

```
app.py                  # Serveur Flask + API /api/best-moves
src/scrabble/
  board.py              # Plateau 15x15 et cases bonus
  values.py             # Valeurs des lettres (Scrabble français)
  dictionary.py         # Chargement du dictionnaire dans un trie
  solver.py             # Recherche du meilleur coup (DFS + élagage par trie)
templates/index.html    # Page de l'interface
static/style.css         # Style du plateau et des composants
static/app.js            # Logique du plateau côté client
words.txt                # Dictionnaire français (one word per line)
```

## Utilisation en script

```python
import sys
sys.path.insert(0, "src")
from scrabble import create_empty_board, load_dictionary, find_best_moves

board = create_empty_board()
dictionary = load_dictionary()
moves = find_best_moves(board, list("chatsel"), dictionary, limit=5)
for move in moves:
    print(move.word, move.score, move.direction, move.row, move.col)
```
