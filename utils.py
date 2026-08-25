from moves import is_square_attacked, legal_moves
piece_value = {
    "P": 100,
    "N": 300,
    "B": 320,
    "R": 500,
    "Q": 900,
    "K": 0
}

piece_display = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
    ".": "·"
}

ranks = {
    "8": 0, "7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7
}

files = {
    "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
}

knight_offsets = [
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2)
]

def convert(square):
    col = files[square[0]]
    row = ranks[square[1]]
    return row, col

def notation(row, col):
    switch = {y:x for x, y in files.items()}
    rank = 8 - row
    file = switch[col]
    return str(file) + str(rank)

def game_phase(board):
    max = 24
    current = 0
    for row in board.squares:
        for piece in row:
            if piece.upper == "N":
                current += 1
            elif piece.upper == "B":
                current +=1
            elif piece.upper == "R":
                current += 2
            elif piece.upper == "Q":
                current += 4
    if current > max:
        current = max
    return current, max

def is_checkmate(board, is_white):
    king = board.white_king if is_white else board.black_king
    in_check =  is_square_attacked(board, king, not board.is_white)
    return in_check and len(legal_moves(board, board.is_white)) == 0

def is_stalemate(board, is_white):
    king = board.white_king if is_white else board.black_king
    in_check =  is_square_attacked(board, king, not board.is_white)
    return (not in_check) and len(legal_moves(board, board.is_white)) == 0

def convert_SAN(board, start, end, promote=None):
    info = board.classify_move(start, end, promote)
    piece_letters = {
    "N": "N",
    "B": "B",
    "R": "R",
    "Q": "Q",
    "K": "K"
    }
    piece = info["piece"]
    _, start_col = start
    end_row, end_col = end
    new_f = {y:x for x, y in files.items()}
    new_r = {y:x for x,y in ranks.items()}
    file = new_f[end_col]
    rank = new_r[end_row]
    is_capture = (info["captured"] != "." or info["is_en_passant"])
    promotion = ""
    if piece.upper() == "P":
        if is_capture:
            letter = new_f[start_col]
        else:
            letter = ""
    elif piece != ".":
        letter = piece_letters[piece.upper()]
    
    captured = "x" if is_capture else ""

    square = file + rank
    if info["is_castling"]:
        if end_col == 6:
            return "O-O"
        else:
            return "O-O-O"
    if info["promotion"]:
        promotion = f"={info['promotion'].upper()}"
    SAN = f"{letter}{captured}{square}{promotion}"
    return SAN
    
