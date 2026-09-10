"""
chess_gui.py

A simple graphical interface for the chess bot, built with pygame.
Click a piece, then click a destination square to move it there. The
bot automatically replies using the same engine as chess_bot.py.

Run:
    python chess_gui.py
"""

import sys
import chess
import pygame

from chess_bot import get_bot_move

SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
WINDOW_SIZE = (BOARD_SIZE, BOARD_SIZE + 40)  # extra strip for status text

LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (246, 246, 105)
LEGAL_DOT = (30, 30, 30)
STATUS_BG = (40, 40, 40)
STATUS_TEXT = (255, 255, 255)

UNICODE_PIECES = {
    "P": "\u2659", "N": "\u2658", "B": "\u2657", "R": "\u2656", "Q": "\u2655", "K": "\u2654",
    "p": "\u265F", "n": "\u265E", "b": "\u265D", "r": "\u265C", "q": "\u265B", "k": "\u265A",
}


def square_to_pixel(square, flipped):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    if flipped:
        file = 7 - file
        rank = 7 - rank
    x = file * SQUARE_SIZE
    y = (7 - rank) * SQUARE_SIZE
    return x, y


def pixel_to_square(pos, flipped):
    x, y = pos
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    if flipped:
        file = 7 - file
        rank = 7 - rank
    if 0 <= file <= 7 and 0 <= rank <= 7:
        return chess.square(file, rank)
    return None


def draw_board(screen, board, font, selected_square, legal_targets, flipped):
    for square in chess.SQUARES:
        x, y = square_to_pixel(square, flipped)
        is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
        color = LIGHT if is_light else DARK
        pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        if square == selected_square:
            pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

        piece = board.piece_at(square)
        if piece:
            symbol = UNICODE_PIECES[piece.symbol()]
            color_rgb = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
            outline = font.render(symbol, True, (128, 128, 128))
            text = font.render(symbol, True, color_rgb)
            rect = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
            screen.blit(outline, rect.move(1, 1))
            screen.blit(text, rect)

        if square in legal_targets:
            center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
            pygame.draw.circle(screen, LEGAL_DOT, center, 10)


def draw_status(screen, font, text):
    pygame.draw.rect(screen, STATUS_BG, (0, BOARD_SIZE, BOARD_SIZE, 40))
    surface = font.render(text, True, STATUS_TEXT)
    screen.blit(surface, (10, BOARD_SIZE + 8))


def choose_color():
    choice = input("Play as (w)hite or (b)lack? [w]: ").strip().lower()
    return choice != "b"


def legal_targets_from(board, square):
    return [m.to_square for m in board.legal_moves if m.from_square == square]


def build_move(board, from_square, to_square):
    """Return a legal move between two squares, auto-promoting to queen."""
    move = chess.Move(from_square, to_square)
    if move in board.legal_moves:
        return move
    promo_move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
    if promo_move in board.legal_moves:
        return promo_move
    return None


def main():
    human_is_white = choose_color()
    depth_input = input("Bot search depth (2-4 recommended, default 3): ").strip()
    depth = int(depth_input) if depth_input.isdigit() else 3

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Chess Bot")
    piece_font = pygame.font.SysFont("segoeuisymbol", 56)
    status_font = pygame.font.SysFont("arial", 18)
    clock = pygame.time.Clock()

    board = chess.Board()
    flipped = not human_is_white
    selected_square = None
    legal_targets = []
    status = "Your move" if human_is_white else "Bot is thinking..."

    def redraw():
        draw_board(screen, board, piece_font, selected_square, legal_targets, flipped)
        draw_status(screen, status_font, status)
        pygame.display.flip()

    def bot_move_if_needed():
        nonlocal status
        if board.is_game_over() or (board.turn == chess.WHITE) == human_is_white:
            return
        status = "Bot is thinking..."
        redraw()
        move = get_bot_move(board, depth)
        if move:
            board.push(move)
        status = f"Game over: {board.result()}" if board.is_game_over() else "Your move"

    bot_move_if_needed()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
                if (board.turn == chess.WHITE) != human_is_white:
                    continue  # bot's turn, ignore clicks

                clicked_square = pixel_to_square(event.pos, flipped)
                if clicked_square is None:
                    continue

                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                        legal_targets = legal_targets_from(board, clicked_square)
                elif clicked_square == selected_square:
                    selected_square = None
                    legal_targets = []
                else:
                    move = build_move(board, selected_square, clicked_square)
                    if move:
                        board.push(move)
                        selected_square = None
                        legal_targets = []
                        status = f"Game over: {board.result()}" if board.is_game_over() else "Bot is thinking..."
                        redraw()
                        bot_move_if_needed()
                    else:
                        piece = board.piece_at(clicked_square)
                        if piece and piece.color == board.turn:
                            selected_square = clicked_square
                            legal_targets = legal_targets_from(board, clicked_square)
                        else:
                            selected_square = None
                            legal_targets = []

        redraw()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
