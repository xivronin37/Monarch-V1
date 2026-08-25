
def generate_knight_moves(board, row, col):
    from utils import knight_offsets
    moves = []
    piece = board.squares[row][col]
    for x, y in knight_offsets:
        new_x = row + x
        new_y = col + y
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            target = board.squares[new_x][new_y]
            if (target == "." or piece.isupper() != target.isupper()) and target.upper() != "K":
                moves.append(((row, col), (new_x, new_y)))
    return moves

def generate_rook_moves(board, row, col):
    possible = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    piece = board.squares[row][col]
    moves = []
    for x, y in possible:
        r, c = row, col
        while True:
            r += x
            c += y
            if not (0 <= r < 8 and 0 <= c < 8):
                break
            target = board.squares[r][c]
            if target == ".":
                moves.append(((row, col), (r,c)))
            elif target.isupper() != piece.isupper() and target.upper() != "K":
                    moves.append(((row, col), (r, c)))
                    break
            else:
                break
    return moves

def generate_bishop_moves(board, row, col):
    possible = [(-1, -1), (-1,  1), (1,  -1), (1,   1)]   
    piece = board.squares[row][col]
    moves = []
    for x, y in possible:
        r, c = row, col
        while True:
            r += x
            c += y
            if not (0 <= r < 8 and 0 <= c < 8):
                break
            target = board.squares[r][c]
            if target == ".":
                moves.append(((row, col), (r,c)))
            elif target.isupper() != piece.isupper() and target.upper() != "K":
                    moves.append(((row, col), (r, c)))
                    break
            else:
                break
    return moves

def generate_queen_moves(board, row, col):
    return generate_rook_moves(board, row, col) + generate_bishop_moves(board, row, col)

def generate_king_moves(board, row, col):
    king_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),(1, -1),  (1, 0),  (1, 1)]   
    piece = board.squares[row][col]
    moves = []
    for x, y in king_offsets:
        r = row + x
        c = col + y
        if 0 <= r < 8 and 0 <= c < 8:
            target = board.squares[r][c]
            if target == ".":
                moves.append(((row, col), (r, c)))
            elif target.isupper() != piece.isupper() and target.upper() != "K":
                    moves.append(((row, col), (r, c)))
    return moves

def generate_pawn_moves(board, row, col):
    moves = []
    piece = board.squares[row][col]
    is_white = True if piece.isupper() else False
    direction = -1 if piece.isupper() else 1
    start_row = 6 if direction == -1 else 1
    one_step = row + direction
    if 0 <= one_step < 8 and board.squares[one_step][col] == ".":
        moves.append(((row, col), (one_step, col)))
        two_steps = row + direction * 2
        if row == start_row and board.squares[two_steps][col] == ".":
            moves.append(((row, col), (two_steps, col)))
    for offset in [-1, 1]:
        c_row = row + direction
        c_col = col + offset
        if 0 <= c_row < 8 and 0 <= c_col < 8:
            target = board.squares[c_row][c_col]
            if target != "." and target.isupper() != piece.isupper() and target.upper() != "K":
                moves.append(((row, col), (c_row, c_col)))
    captured_row = row + 1 if is_white else row - 1
    if ((captured_row), (col+1)) == board.en_passant:
        moves.append(((row, col), ((captured_row), (col+1))))
    elif ((captured_row), (col-1)) == board.en_passant:
        moves.append(((row, col), ((captured_row), (col-1))))
    return moves

def generate_pawn_attacks(board, row, col):
    moves = []
    piece = board.squares[row][col]
    direction = -1 if piece.isupper() else 1
    for offset in [-1, 1]:
        c_row = row + direction
        c_col = col + offset
        if 0 <= c_row < 8 and 0 <= c_col < 8:
            target = board.squares[c_row][c_col]
            if target != "." and target.isupper() != piece.isupper():
                moves.append((c_row, c_col))
    return moves


def psuedo_legal_moves(board, is_white):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.squares[row][col]
            if piece.isupper() != is_white:
                continue
            if piece.upper() == "N":
                moves.extend(generate_knight_moves(board, row, col))
            elif piece.upper() == "B":
                moves.extend(generate_bishop_moves(board, row, col))
            elif piece.upper() == "R":
                moves.extend(generate_rook_moves(board, row, col))
            elif piece.upper() == "Q":
                moves.extend(generate_queen_moves(board, row, col))
            elif piece.upper() == "P":
                moves.extend(generate_pawn_moves(board, row, col))
            elif piece.upper() == "K":
                moves.extend(generate_king_moves(board, row, col))
    return moves

def is_square_attacked(board, square, by_white):
    sq_row, sq_col = square
    from utils import knight_offsets
    piece = board.squares[sq_row][sq_col]
    for x, y in knight_offsets:
        new_x = sq_row + x
        new_y = sq_col + y
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            target = board.squares[new_x][new_y]
            if target == ".":
                continue
            if target.upper() == "N" and target.isupper() == by_white:
                return True
    rook_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for x, y in rook_offsets:
        r, c = sq_row, sq_col
        while True:
            r += x
            c += y
            if not (0 <= r < 8 and 0 <= c < 8):
                break
            target = board.squares[r][c]
            if target == ".":
                continue
            if target.upper() in ("R", "Q") and target.isupper() == by_white:
                return True
            
            break

    bishop_offsets = [(-1, -1), (-1,  1), (1,  -1), (1,   1)]   
    for x, y in bishop_offsets:
        r, c = sq_row, sq_col
        while True:
            r += x
            c += y
            if not (0 <= r < 8 and 0 <= c < 8):
                break
            target = board.squares[r][c]
            if target == ".":
                continue
            if target.upper() in ("B", "Q") and target.isupper() == by_white:
                return True
            
            break

    direction = 1 if by_white else -1
    for offset in [-1, 1]:
        c_row = sq_row + direction
        c_col = sq_col + offset
        if 0 <= c_row < 8 and 0 <= c_col < 8:
            target = board.squares[c_row][c_col]
            enemy_pawn = "P" if by_white else "p"
            if target == enemy_pawn:
                return True
    king_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),(1, -1),  (1, 0),  (1, 1)]   
    for x, y in king_offsets:
        r = sq_row + x
        c = sq_col + y
        if 0 <= r < 8 and 0 <= c < 8:
            target = board.squares[r][c]
            if target == ".":
                continue
            if target.upper() == "K" and target.isupper() == by_white:
                return True
    return False

def is_legal_move(board, start, end, is_white):
    from utils import convert
    if isinstance(start, str):
        start_row, start_col = convert(start)
    elif isinstance(start, tuple):
        start_row, start_col = start
    if isinstance(end, str):
        end_row, end_col = convert(end)
    elif isinstance(end, tuple):
        end_row, end_col = end

    piece = board.squares[start_row][start_col]

    if piece == "." or piece.isupper() != is_white:
        return False
    
    if not board.make_move(start, end):
        return False

    if is_white:
        in_check = is_square_attacked(board, board.white_king, False)
    else:
        in_check = is_square_attacked(board, board.black_king, True)
    board.unmake_move()

    return not in_check

def legal_moves(board, is_white):
    legal= []
    psuedo = psuedo_legal_moves(board, is_white)
    for start, end in psuedo:
        start_row, start_col = start
        piece = board.squares[start_row][start_col]
        if piece == ".":
            continue
        if piece.isupper() != is_white:
            continue
        if is_legal_move(board, start, end, is_white):
            legal.append((start, end))
    return legal
