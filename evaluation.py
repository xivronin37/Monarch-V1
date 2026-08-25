from utils import game_phase, piece_value
from tables import table

def evaluate(board):
    middlegame = 0
    endgame = 0
    score = 0
    current, max = game_phase(board)
    for row in range(8):
        for col in range(8):
            piece = board.squares[row][col]
            if piece == ".":
                continue
            value = piece_value[piece.upper()]
            if piece.isupper():
                score += value
            else:
                score -= value
            if piece == "P":
                score += table.pawn[row][col]
            elif piece == "p":
                score -= table.pawn[7-row][col]
            if piece == "N":
                score += table.knight[row][col]
            elif piece == "n":
                score -= table.knight[7-row][col]
            if piece == "B":
                score += table.bishop[row][col]
            elif piece == "b":
                score -= table.bishop[7-row][col]
            if piece == "R":
                score += table.rook[row][col]
            elif piece == "r":
                score -= table.rook[7-row][col]
            if piece == "Q":
                score += table.queen[row][col]
            elif piece == "q":
                score -= table.queen[7-row][col]
            if piece == "K":
                middlegame += table.king_middle[row][col]
                endgame += table.king_end[row][col]
            elif piece == "k":
                middlegame -= table.king_middle[7-row][col]
                endgame -= table.king_end[row][col]
    king_eval = ((middlegame * current) + (endgame *(max - current))) / max
    score += king_eval
    return score / 100

