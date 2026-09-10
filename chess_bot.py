"""
chess_bot.py

A simple chess-playing bot.

Uses the python-chess library to handle the board and legal moves, and a
hand-written minimax search with alpha-beta pruning to pick moves. The
evaluation function is basic: material count + simple piece-square tables
that encourage pawns/knights toward better squares.

Play against it from the command line:
    python chess_bot.py
"""

import sys
import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Encourage central/advanced development for pawns and knights.
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
}


def evaluate(board: chess.Board) -> int:
    """Positive scores favor White, negative favor Black."""
    if board.is_checkmate():
        # The side to move has been checkmated.
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]
        table = PIECE_SQUARE_TABLES.get(piece.piece_type)
        positional_bonus = 0
        if table:
            idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
            positional_bonus = table[idx]

        total = value + positional_bonus
        score += total if piece.color == chess.WHITE else -total

    return score


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board), None

    best_move = None

    if maximizing:
        best_score = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = float("inf")
        for move in board.legal_moves:
            board.push(move)
            score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if score < best_score:
                best_score, best_move = score, move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score, best_move


def get_bot_move(board: chess.Board, depth: int = 3) -> chess.Move:
    _, move = minimax(board, depth, -float("inf"), float("inf"), board.turn == chess.WHITE)
    return move


def parse_user_move(board: chess.Board, text: str):
    """Accept either SAN ('Nf3') or UCI ('g1f3') input."""
    try:
        return board.parse_san(text)
    except ValueError:
        pass
    try:
        move = chess.Move.from_uci(text)
        if move in board.legal_moves:
            return move
    except ValueError:
        pass
    return None


def main():
    print("Simple Chess Bot")
    print("================")
    print("Enter moves in SAN (e.g. Nf3) or UCI (e.g. g1f3). Type 'quit' to exit.\n")

    depth_input = input("Bot search depth (2-4 recommended, default 3): ").strip()
    depth = int(depth_input) if depth_input.isdigit() else 3

    color_input = input("Play as (w)hite or (b)lack? [w]: ").strip().lower()
    human_is_white = color_input != "b"

    board = chess.Board()

    while not board.is_game_over():
        print()
        print(board)
        print()

        human_turn = (board.turn == chess.WHITE) == human_is_white

        if human_turn:
            text = input("Your move: ").strip()
            if text.lower() == "quit":
                sys.exit(0)
            move = parse_user_move(board, text)
            if move is None:
                print("Invalid move, try again.")
                continue
            board.push(move)
        else:
            print("Bot is thinking...")
            move = get_bot_move(board, depth)
            if move is None:
                break
            print(f"Bot plays: {board.san(move)}")
            board.push(move)

    print()
    print(board)
    print()
    print("Game over:", board.result())
    print(board.outcome())


if __name__ == "__main__":
    main()
