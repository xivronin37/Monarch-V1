from evaluation import evaluate
from moves import legal_moves
from utils import piece_value, is_checkmate, is_stalemate
from board import board
import time
class SearchEngine:
    def __init__(self):
        self.nodes = 0

    def negamax(self, board, depth, alpha, beta, is_white, start_time, time_limit, ply=0, previous_best=None):
        self.nodes += 1
        if time.perf_counter() - start_time >= time_limit:
            raise TimeoutError
        mate_score = 10000
        if depth == 0:
            final_score = evaluate(board)
            return final_score, None
        if is_checkmate(board, is_white):
            return -mate_score + ply, None
        if is_stalemate(board, is_white):
            return 0
        moves = legal_moves(board, is_white)
        scored_moves = []
        for move in moves:
            start, end = move
            start_row, start_col = start
            end_row, end_col = end
            piece = board.squares[start_row][start_col]
            target = board.squares[end_row][end_col]
            if target != ".":
                score = 10 + piece_value[target.upper()] - piece_value[piece.upper()]
            else:
                score = 0
            scored_moves.append((score, move))
        if depth <= 2:
            if previous_best is None:
                scored_moves.sort(reverse=True)
            scored_moves.sort(key=lambda x: x[1] == previous_best ,reverse=True)

        best_score = float("-inf")
        best_move = None
        for _, move in scored_moves:
            try:
                start, end = move
                board.make_move(start, end)
                child_score, _ = self.negamax(board, depth - 1, -beta, -alpha, not is_white, start_time, time_limit, ply + 1)
            finally:
                board.unmake_move()
            
            score = -child_score
            
            if score > best_score:
                best_move = (start, end)
                best_score = score

            alpha = max(alpha, score)

            if alpha >= beta:
                    break
            
        if best_score == 0.0:
            best_score = 0.0

        return best_score, best_move

    def iterative_deepening(self, board, max_time=2.0):
        self.nodes = 0
        start_time = time.perf_counter()
        best_move = None
        best_score = None
        depth = 1
        while True:
            if time.perf_counter() - start_time >= max_time:
                break
            try:
                score, move = self.negamax(board, depth, float("-inf"), float("inf"), board.is_white, start_time, max_time, previous_best=best_move)
            except TimeoutError:
                break

            if move is not None:
                best_score = score
                best_move = move

            depth += 1

        return best_score, best_move, depth