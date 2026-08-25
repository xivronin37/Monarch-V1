from utils import piece_display
from moves import is_square_attacked

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
class Board:
    def __init__(self):
        self.squares = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.debug_depth = 0
        self.is_white = True
        self.en_passant = None
        self.move_history = []
        self.castling_rights = {
            "K": True,
            "Q": True,
            "k": True,
            "q": True
        }
        self.squares = self.parse_fen(fen)
        self.half_move_clock = 0
        self.full_move_clock = 0

    def parse_fen(self, fen):
        board = []
        fields= fen.split(" ")
        pieces = fields[0].split("/")
        active_color = fields[1]
        castling_rights = fields[2]
        en_passant_target = fields[3]
        half_move = int(fields[4])
        full_move = int(fields[5])
        for row in pieces:
            current = []
            for char in row:
                if char.isdigit():
                    current.extend(["."] * int(char))
                else:
                    current.append(char)
            board.append(current)

        if "w" in active_color:
            self.is_white = True
        elif "b" in active_color:
            self.is_white = False

        self.castling_rights["K"] = "K" in castling_rights
        self.castling_rights["Q"] = "Q" in castling_rights
        self.castling_rights["k"] = "k" in castling_rights
        self.castling_rights["q"] = 'q' in castling_rights

        if "-" in en_passant_target:
            self.en_passant = None
        else:
            self.en_passant = en_passant_target

        self.half_move_clock = half_move
        self.full_move_clock = full_move

        return board

    def to_fen(self):
        fen_rows = []
        for row in self.squares:
            r = ""
            empty = 0
            for piece in row:
                if piece != ".":
                    if empty > 0:
                        r += str(empty)
                        empty = 0
                    r += str(piece)
                else:
                    empty += 1
            if empty > 0:
                r += str(empty)
            fen_rows.append(r)
        board_fen = "/".join(fen_rows)
        color = "w" if self.is_white else "b"
        final_fen = f"{board_fen} {color} {self.is_white} {self.castling_rights} {self.en_passant} {self.half_move_clock} {self.full_move_clock}"
        return final_fen
    
    def display(self):
        for row in self.squares:
            print(" ".join(piece_display[p] for p in row))
    
    def is_empty(self, coordinates):
        row, col = coordinates
        target = self.squares[row][col]
        if target == ".":
            return True
        
    def can_castle(self, board, is_white):
        castling = []
        w_queenside = [(7,1), (7,2), (7,3)]
        w_kingside = [(7,5), (7,6)]
        b_kingside = [(0,5), (0,6)]
        b_queenside = [(0,1), (0,2), (0,3)]
        if is_white:
            if is_square_attacked(board, (7,4), False):
                return False
            if all(self.is_empty(square) for square in w_queenside) and self.castling_rights["Q"]:
                if not is_square_attacked(board, (7,2), False) and not is_square_attacked(board, (7,3), False):
                    castling.append("Q")
            if all(self.is_empty(square) for square in w_kingside) and self.castling_rights["K"]:
                if all(not is_square_attacked(board, square, False) for square in w_kingside):
                    castling.append("K")
        if not is_white:
            if is_square_attacked(board, (0, 4), True):
                return False
            if all(self.is_empty(square) for square in b_kingside) and self.castling_rights["k"]:
                if all(not is_square_attacked(board, square, True) for square in b_kingside):
                    castling.append("k")
            elif all(self.is_empty(square) for square in b_queenside) and self.castling_rights["q"]:
                if not is_square_attacked(board, (0,2), True) and not is_square_attacked(board, (0,3), True):
                    castling.append("q")
        return castling
    
    def make_move(self, start, end, promote=None):
        if not board.is_white:
            self.full_move_clock += 1
        start_row, start_col = start
        end_row, end_col = end
        piece = self.squares[start_row][start_col]
        captured = self.squares[end_row][end_col]

        if piece.upper() == "P":
            self.half_move_clock = 0
        else:
            self.half_move_clock += 1

        if piece == ".":
            return False
        if captured != "." and (captured.isupper() == self.is_white):
            return False
        
        info = self.classify_move(start, end, promote)
        if info is None:
            return False
        if info["is_en_passant"]:
            captured_row = end_row + 1 if self.is_white else end_row - 1
            captured = self.squares[captured_row][end_col]
        else:
            captured = self.squares[end_row][end_col]
        move_record = {
            "start": start,
            "end": end,
            "is_white": self.is_white,
            "white_king": self.white_king,
            "black_king": self.black_king,
            "castling_rights": self.castling_rights.copy(),
            "rook_start": None,
            "rook_end": None,
            "en_passant": self.en_passant,
            "half_move_clock": self.half_move_clock,
            **info
        }
        self.move_history.append(move_record)
        self.en_passant = None

        self.squares[start_row][start_col] = "."

        if info["is_castling"]:
            if piece == "K":
                castling  = self.can_castle(self, True)
                if end == (7, 6) and "K" in castling:
                    self.squares[7][5] = "R"
                    self.squares[7][6] = "K"
                    self.squares[7][7] = "."
                    move_record["rook_start"] = (7,7)
                    move_record["rook_end"] = (7, 5)
                elif end == (7, 2) and "Q" in castling:
                    self.squares[7][0] = "."
                    self.squares[7][1] = "."
                    self.squares[7][2] = "K"
                    self.squares[7][3] = "R"
                    move_record["is_castling"] = True
                    move_record["rook_start"] = (7, 0)
                    move_record["rook_end"] = (7, 3)
            elif piece == "k":
                castling = self.can_castle(self, False)
                if end == (0, 6) and "k" in castling:
                    self.squares[0][5] = "r"
                    self.squares[0][6] = "k"
                    self.squares[0][7] = "."
                    move_record["rook_start"] = (0, 7)
                    move_record["rook_end"]= (0, 5)
                elif end == (0, 2) and "q" in castling:
                    self.squares[0][0] = "."
                    self.squares[0][1] = "."
                    self.squares[0][2] = "k"
                    self.squares[0][3] = "r"
                    move_record["rook_start"] = (0, 0)
                    move_record["rook_end"] = (0, 3)
        elif info["promotion"]:
            if piece.isupper():
                self.squares[end_row][end_col] = info["promotion"].upper()
                self.squares[start_row][start_col] = "."
            elif piece.islower():
                self.squares[end_row][end_col] = info["promotion"].lower()
                self.squares[start_row][start_col] = "."
        elif info["is_en_passant"]:
            self.squares[start_row][start_col] = "."
            self.squares[captured_row][end_col] = "."
            self.squares[end_row][end_col] = piece
        else:
            self.squares[end_row][end_col] = piece
        if piece == "K":
            self.white_king = (end_row, end_col)
        elif piece == "k":
            self.black_king = (end_row, end_col)
        
        self.update_castling_rights(piece, captured, start, end)
        
        self.is_white = not self.is_white
        return True
    
    def classify_move(self, start, end, promote=None):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.squares[start_row][start_col]
        captured = self.squares[end_row][end_col]
        is_castling = False
        promotion = promote

        if piece == ".":
            return None

        if piece == "K" and abs(end_col - start_col) == 2:
            castling = self.can_castle(self, True)
            if end == (7, 6) and "K" in castling:
                is_castling = True
            elif end == (7, 2) and "Q" in castling:
                is_castling = True

        elif piece == "k" and abs(end_col - start_col) == 2:
            castling = self.can_castle(self, False)
            if end == (0, 6) and "k" in castling:
                is_castling = True
            elif end == (0, 2) and "q" in castling:
                is_castling = True
        
        if piece == "P" and end_row == 0 and promote is not None:
            promotion = promotion.upper()
        elif piece == "p" and end_row == 7 and promote is not None:
            promotion = promotion.lower()

        is_en_passant = (end == self.en_passant)

        return {
            "piece": piece,
            "captured": captured,
            "is_castling": is_castling,
            "promotion": promotion,
            "is_en_passant": is_en_passant
        }
    

        

    
    def unmake_move(self):
        if board.is_white:
            self.full_move_clock -= 1
        if not self.move_history:
            return False
        self.debug_depth -= 1
        move = self.move_history.pop()
        start_row, start_col = move["start"]
        end_row, end_col = move["end"]
        self.squares[start_row][start_col] = move["piece"]
        self.squares[end_row][end_col] = move["captured"]
        self.white_king = move["white_king"]
        self.black_king = move["black_king"]
        self.castling_rights = move["castling_rights"].copy()
        self.en_passant = move["en_passant"]
        if move["is_castling"]:
            s_row, s_col = move["rook_start"]
            e_row, e_col = move["rook_end"]
            self.squares[e_row][e_col] = "."
            if (e_row, e_col) == (7, 5) or (e_row, e_col) == (7,3):
                self.squares[s_row][s_col] = "R"
            elif (e_row, e_col) == (0, 5) or (e_row, e_col) == (0, 3):
                self.squares[s_row][s_col] = "r"
        self.half_move_clock = move["half_move_clock"]
        self.is_white = move["is_white"]

    def update_castling_rights(self, piece, captured, start, end):
        if piece == "K":
            self.castling_rights["K"] = False
            self.castling_rights["Q"] = False
        elif piece == "k":
            self.castling_rights["k"] = False
            self.castling_rights["q"] = False
        if piece == "R":
            if start == (7, 0):
                self.castling_rights["K"] = False
            elif start == (7, 7):
                self.castling_rights["Q"] = False
        elif piece == "r":
            if start == (0, 0):
                self.castling_rights["q"] = False
            elif start == (0, 7):
                self.castling_rights["k"] = False
        if captured == "R":
            if end == (7, 0):
                self.castling_rights["K"] = False
            elif end == (7, 7):
                self.castling_rights["Q"] = False
        elif captured == "r":
            if end == (0, 0):
                self.castling_rights["q"] = False
            elif end == (7,7):
                self.castling_rights["k"] = False

board = Board()