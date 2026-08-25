import pygame
import time
import threading
import copy
from settings import *
from moves import legal_moves, is_square_attacked
from evaluation import evaluate
from board import board
from utils import is_checkmate, is_stalemate, convert_SAN
from search import SearchEngine
from uci import StockfishEngine

monarch_engine = SearchEngine()
stockfish = StockfishEngine()

class GameLoop():

    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        self.score = 0
        self.depth = 0

        self.SAN_history = []
        self.current_move = None
        self.player_move = None

        self.nodes_searched = 0
        self.nps = 0
        self.full_move = 1

        self.is_player = False
        self.player_turn = "White"
        self.selected = None
        self.destination = None
        self.turn_boolean = True if self.player_turn == "White" else False

        self.engine_move = None
        self.engine_thinking = False
        self.lock = threading.Lock()

        self.animating = False
        self.anim_piece = None
        self.anim_start = None
        self.anim_end = None
        self.anim_progress = 0

        self.move_self_sound = pygame.mixer.Sound("Sounds/move-self.wav")
        self.move_opponent_sound = pygame.mixer.Sound("Sounds/move-opponent.wav")
        self.capture_sound = pygame.mixer.Sound("Sounds/capture.wav")
        self.check_sound = pygame.mixer.Sound("Sounds/check.wav")
        self.end_sound = pygame.mixer.Sound("Sounds/game-end.wav")
    
    def run(self):
        clock = pygame.time.Clock()
        piece_names = ["wp", "wn", "wb", "wr", "wq", "wk", "bp", "bn", "bb", "br", "bq", "bk"]
        for name in piece_names:
            image = pygame.image.load(f"Images/{name}.png")
            PIECES[name] = pygame.transform.smoothscale(image, (SQ_SIZE, SQ_SIZE))
        
        def draw_board(screen):
            for r in range(8):
                for c in range(8):
                    color = LIGHT if (r+c) % 2 == 0 else DARK
                    pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

        def draw_pieces(board):
            for r in range(8):
                for c in range(8):

                    if self.animating and (r, c) in (self.anim_start, self.anim_end):
                        continue

                    piece = board.squares[r][c]
                    
                    if piece != ".":
                        if piece.isupper():
                            self.screen.blit(PIECES["w" + piece.lower()], (c * SQ_SIZE, r * SQ_SIZE))
                        else:
                            self.screen.blit(PIECES["b" + piece], (c * SQ_SIZE, r * SQ_SIZE))

            if self.animating:
                piece = self.anim_piece
                start_row, start_col = self.anim_start
                end_row, end_col = self.anim_end

                eased_progress = self.ease_out(self.anim_progress)
                x = self.lerp(start_col, end_col, eased_progress) * SQ_SIZE
                y = self.lerp(start_row, end_row, eased_progress) * SQ_SIZE

                if piece.isupper():
                    img = PIECES["w" + piece.lower()]
                else:
                    img = PIECES["b" + piece]
                
                self.screen.blit(img, (x, y))

        label_turn = self.font.render("Turn: ", True, (255, 255, 255))
        turn_width = label_turn.get_width()

        label_move = self.font.render("Move: ", True, (255, 255, 255))
        move_width = label_move.get_width()

        node_label = self.font.render("Nodes searched: ", True, (255, 255, 255))
        node_width = node_label.get_width()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_player and board.is_white == self.turn_boolean:
                        self.handle_input(event.pos)
            color_string = "White" if board.is_white else "Black"
            color_surface = self.font.render(color_string, True, (255, 255, 255))

            if is_checkmate(board, board.is_white):
                print("Checkmate!")
                self.current_move = "Checkmate!"
                print(" ".join(self.SAN_history))
                self.end_sound.play()
                running = False
            elif is_stalemate(board, board.is_white):
                print("Stalemate!")
                self.current_move = "Stalemate!"
                print(" ".join(self.SAN_history))
                self.end_sound.play()
                running = False

            self.gameplay()
        

            with self.lock:
                if self.engine_move is not None:
                    start, end = self.engine_move
                    end_row, end_col = end
                    target = board.squares[end_row][end_col]
                    self.SAN_history.append(f"{self.full_move}. {convert_SAN(board, start, end)}")
                    self.current_move = convert_SAN(board, start, end)
                    self.full_move += 1

                    self.animating = True
                    self.anim_piece = board.squares[start[0]][start[1]]
                    self.anim_start = start
                    self.anim_end = end
                    self.anim_progress = 0


                    board.make_move(start, end)
                    opponent_king_pos = board.white_king if board.is_white else board.black_king
                    in_check = is_square_attacked(board, opponent_king_pos, not board.is_white)

                    if in_check:
                        self.check_sound.play()
                    elif target != ".":
                        self.capture_sound.play()
                    else:
                        self.move_opponent_sound.play()
                    
                    self.engine_move = None
                    self.engine_thinking = False

            if self.animating:
                self.anim_progress += 0.15

                if self.anim_progress >= 1:
                    self.animating = False
                    self.anim_progress = 0

            self.screen.fill((0,0,0))
            draw_board(self.screen)
            draw_pieces(board)

            pygame.draw.rect(self.screen, (27, 27, 27), (640, 0, 320, HEIGHT))
            if self.current_move:
                display_move = self.font.render(self.current_move, True, (255, 255, 255))
            else:
                display_move = self.font.render("No move played.", True, (255, 255, 255))
            
            eval = self.font.render(f"Evaluation: {str(evaluate(board))}", True, (255, 255, 255))
            label_history = self.font.render("Move History", True, (255, 255, 255))

            if not board.is_white:
                display_depth = self.font.render(f"Depth: {str(self.depth)}", True, (255, 255, 255))
                self.screen.blit(display_depth, (660, 60))
            else:
                display_depth = self.font.render("Depth: None", True, (255, 255, 255))
                self.screen.blit(display_depth, (660, 60))

            display_nodes = self.font.render(str(self.nodes_searched), True, (255, 255, 255))
            display_nps = self.font.render(f"Nodes per second: {str(self.nps)}", True, (255, 255, 255))

            self.screen.blit(label_turn, (660, 20))
            self.screen.blit(color_surface, (660 + turn_width, 20))
            self.screen.blit(label_move, (660, 40))
            self.screen.blit(display_move, (660 + move_width, 40))
            self.screen.blit(node_label, (660, 80))
            self.screen.blit(display_nodes, (660 + node_width, 80))
            self.screen.blit(display_nps, (660, 100))
            self.screen.blit(eval, (660, 120))
            self.screen.blit(label_history, (660, 180))

            y = 200
            visible_moves = self.SAN_history[-36:]
            for i in range(0, len(visible_moves), 2):
                white = visible_moves[i]

                if i + 1 < len(visible_moves):
                    black = visible_moves[i + 1]
                else:
                    black = ""

                line = f"{white:<10} {black}"

                text = self.font.render(line, True, (255,255,255))
                self.screen.blit(text, (660, y))
                y += 22

            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

    def handle_input(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        col = mouse_x // SQ_SIZE
        row = mouse_y // SQ_SIZE
        piece = board.squares[row][col]
        if self.selected is None:
            if piece != "." and piece.isupper() == self.turn_boolean:
                self.selected = (row, col)
                return
        start = self.selected 
        end = (row, col)
        if piece != "." and piece.isupper() == self.turn_boolean:
            self.selected = (row, col)
            return
        
        if (start, end) in legal_moves(board, self.turn_boolean):
            self.current_move = convert_SAN(board, start, end)
            self.player_move = self.current_move

            if self.player_turn == "White":
                self.SAN_history.append(f"{self.full_move}. {convert_SAN(board, start, end)}")
                self.full_move += 1
            else:
                self.SAN_history.append(self.current_move)
            self.animating = True
            self.anim_piece = board.squares[start[0]][start[1]]
            self.anim_start = start
            self.anim_end = end
            self.anim_progress = 0

            end_row, end_col = end
            target = board.squares[end_row][end_col]

            board.make_move(start, end)
            opponent_king_pos = board.white_king if board.is_white else board.black_king
            in_check = is_square_attacked(board, opponent_king_pos, not board.is_white)

            if in_check:
                self.check_sound.play()
            elif target != ".":
                self.capture_sound.play()
            else:
                self.move_self_sound.play()
            
        self.selected = None
            



    def gameplay(self):
        
        if self.is_player:
            if board.is_white == self.turn_boolean:
                self.reset_stats()
            else:
                self.start_engine()

        else:
            if board.is_white:
                self.start_engine()
            else:
                time.sleep(0.5)
                stockfish.setpos(board.to_fen())
                engine_start, engine_end, engine_promote = stockfish.get_best_move(15)
                end_row, end_col = engine_end
                target = board.squares[end_row][end_col]

                self.current_move = convert_SAN(board, engine_start, engine_end)
                self.SAN_history.append(str(convert_SAN(board, engine_start, engine_end)))

                board.make_move(engine_start, engine_end, engine_promote)
                
                opponent_pos = board.white_king if board.is_white else board.black_king
                in_check = is_square_attacked(board, opponent_pos, not board.is_white)

                if in_check:
                    self.check_sound.play()
                elif target != ".":
                    self.capture_sound.play()
                else:
                    self.move_self_sound.play()

                self.reset_stats()
    
    def engine_worker(self):
        board_copy = copy.deepcopy(board)
        score, move, depth = monarch_engine.iterative_deepening(board_copy)
        with self.lock:
            self.engine_move = move
            self.engine_thinking = True
        self.score = score
        self.depth = depth
        self.nodes_searched = monarch_engine.nodes
        self.nps = self.nodes_searched / 2

    def start_engine(self):
        if self.engine_thinking:
            return
        
        self.engine_thinking = True
        thread = threading.Thread(target=self.engine_worker)
        thread.start()

    def lerp(self, a, b, t):
        return a + (b - a) * t
    
    def ease_out(self, progress):
        return 1 - (1 - progress) * (1 - progress)


    def reset_stats(self):
        self.score = 0
        self.depth = 0
        self.nodes_searched = 0
        self.nps = 0