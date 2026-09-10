# Simple Chess Bot

A command-line chess bot written in Python. It uses the
[`python-chess`](https://python-chess.readthedocs.io/) library to handle
board state and legal moves, and a minimax search with alpha-beta pruning
to choose its moves.

## Setup

1. Make sure you have Python 3.8+ installed.
2. Install the dependency:
   ```
   pip install -r requirements.txt
   ```

## Play

```
python chess_bot.py
```

You'll be asked:
- How deep the bot should search (higher = stronger but slower; 3 is a
  good default).
- Whether you want to play White or Black.

Enter your moves in standard algebraic notation (e.g. `Nf3`, `e4`) or UCI
notation (e.g. `g1f3`, `e2e4`).

## How it works

- **Evaluation**: counts material (pawn = 100, knight/bishop = ~320-330,
  rook = 500, queen = 900) plus a small positional bonus for pawns and
  knights on good squares.
- **Search**: minimax with alpha-beta pruning explores possible move
  sequences a few moves deep and picks the line that leads to the best
  evaluation, assuming the opponent also plays well.

## Ideas for improving it

- Add piece-square tables for bishops, rooks, and the king.
- Add move ordering (try captures first) to make alpha-beta pruning more
  effective at deeper search depths.
- Add an opening book for the first few moves.
- Add iterative deepening with a time limit instead of a fixed depth.
